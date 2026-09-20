const {chromium} = require('/private/tmp/collab-qa-tools/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const OUT = __dirname;
const BASE = 'http://127.0.0.1:3100';
const API = 'http://127.0.0.1:5101';
const results = [];
const events = [];
const pages = {};
const phase = process.argv[2] || 'pages-chat';
const tag = 'QA-' + Date.now();
let browser;
function save() {
  fs.writeFileSync(path.join(OUT, `results-${phase}.json`), JSON.stringify({phase,tag,base:BASE,results,events},null,2));
}
async function check(name, fn) {
  const start = Date.now();
  try {
    const detail = await fn();
    results.push({name,status:'PASS',detail,ms:Date.now()-start});
    console.log('PASS',name,JSON.stringify(detail || ''));
  } catch (e) {
    const record={name,status:'FAIL',detail:e.message,ms:Date.now()-start,screenshots:[]};
    for (const [who,p] of Object.entries(pages)) {
      if (p.isClosed()) continue;
      const filename=`${phase}-${results.length}-${who}.png`;
      await p.screenshot({path:path.join(OUT,'screenshots',filename),fullPage:true,timeout:5000}).then(()=>record.screenshots.push(filename)).catch(()=>{});
    }
    results.push(record);
    console.log('FAIL',name,e.message.split('\n').slice(0,3).join(' '));
  }
  save();
}
async function actor(who, opts={}) {
  const context=await browser.newContext({viewport:{width:1440,height:1000},locale:'de-CH',timezoneId:'Europe/Zurich',...opts});
  const p=await context.newPage();
  p.setDefaultTimeout(5000);
  p.on('pageerror',e=>events.push({who,type:'js',url:p.url(),error:e.message}));
  p.on('response',r=>{if(r.status()>=400)events.push({who,type:'http',status:r.status(),url:r.url()});});
  p.on('requestfailed',r=>events.push({who,type:'network',url:r.url(),error:r.failure()?.errorText}));
  p.on('dialog',async d=>{events.push({who,type:'dialog',message:d.message()});await d.accept();});
  pages[who]=p;
  return p;
}
async function go(p,route) {
  const response=await p.goto(BASE+route,{waitUntil:'domcontentloaded'});
  await p.waitForTimeout(350);
  return response;
}
async function login(p,name,password) {
  await go(p,'/login');
  await p.locator('#username').fill(name);
  await p.locator('#password').fill(password);
  await p.getByRole('button',{name:'Einloggen',exact:true}).click();
  await p.waitForURL('**/start');
}
async function contains(p,selector,text,timeout=5000) {
  await p.locator(selector).filter({hasText:text}).first().waitFor({timeout});
}
async function shot(p,name) {await p.screenshot({path:path.join(OUT,'screenshots',name+'.png'),fullPage:true});}
async function openChat(p,other) {
  await go(p,'/chats');
  await p.locator('.chat-user-name').getByText(other,{exact:true}).click();
  await p.locator('#msgInput').waitFor();
}
async function main() {
  browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'});
  const bob=await actor('bob');
  const alice=await actor('alice');
  await check('Login Bob über Formular',async()=>{await login(bob,'bob','5678');return {url:bob.url()};});
  await check('Login Alice in unabhängiger Sitzung',async()=>{await login(alice,'alice','1234');return {url:alice.url()};});
  if(phase==='pages-chat') {
    const routes=['/start','/projects','/projects/new','/tasks/new','/users','/profile/2','/profile/1','/team/1','/team/2','/team_manage','/teams/new','/chat/1','/chats','/private_chat/1','/register','/login'];
    const inventory=[];
    for(const route of routes) await check('Seite '+route,async()=>{
      const r=await go(bob,route);
      assert.equal(r.status(),200);
      const state=await bob.evaluate(()=>({title:document.title,text:document.body.innerText,links:[...document.querySelectorAll('a[href]')].map(a=>({text:a.innerText,href:a.getAttribute('href')})),forms:[...document.forms].map(f=>({id:f.id,action:f.getAttribute('action'),fields:[...f.elements].map(e=>({tag:e.tagName,id:e.id,name:e.name,type:e.type}))})),width:innerWidth,scrollWidth:document.documentElement.scrollWidth}));
      inventory.push({route,...state});
      await shot(bob,'page-'+route.replaceAll('/','-'));
      return {title:state.title,forms:state.forms.length};
    });
    fs.writeFileSync(path.join(OUT,'page-inventory.json'),JSON.stringify(inventory,null,2));
    const m1=tag+' Bob → Alice äöü 🙂';
    const m2=tag+' Alice → Bob Antwort';
    await check('Privatchat /chats: Bob sendet Alice',async()=>{await openChat(bob,'alice');await openChat(alice,'bob');await bob.locator('#msgInput').fill(m1);await bob.getByRole('button',{name:'Senden',exact:true}).click();await contains(bob,'.chat-msg-bubble',m1);});
    await check('Privatchat: Alice empfängt ohne Neuladen',async()=>{await contains(alice,'.chat-msg-bubble',m1,6000);});
    await check('Privatchat: Alice empfängt nach erneutem Öffnen',async()=>{await openChat(alice,'bob');await contains(alice,'.chat-msg-bubble',m1);});
    await check('Privatchat: Alice antwortet Bob',async()=>{await alice.locator('#msgInput').fill(m2);await alice.getByRole('button',{name:'Senden',exact:true}).click();await contains(alice,'.chat-msg-bubble',m2);await openChat(bob,'alice');await contains(bob,'.chat-msg-bubble',m2);await shot(bob,'chat-bob');await shot(alice,'chat-alice');});
    await check('Privatchat: Nachrichten bleiben nach Neuladen erhalten',async()=>{await openChat(bob,'alice');await contains(bob,'.chat-msg-bubble',m1);await contains(bob,'.chat-msg-bubble',m2);});
    await check('Privatchat aus fremdem Profil öffnen und Verlauf laden',async()=>{await go(bob,'/profile/1');await bob.getByRole('button',{name:'💬 Privater Chat'}).click();await bob.waitForURL('**/private_chat/1');await contains(bob,'#messages',m1);});
    await check('Privatchat aus Profil: Senden funktioniert',async()=>{await bob.locator('#msgInput').fill(tag+' direct');const response=bob.waitForResponse(r=>r.url().endsWith('/chat/private/send')&&r.request().method()==='POST');await bob.getByRole('button',{name:'Senden',exact:true}).click();const r=await response;assert.equal(r.status(),200,`Senden liefert HTTP ${r.status()}`);await contains(bob,'#messages',tag+' direct');});
    const tm1=tag+' Teamnachricht von Bob';
    const tm2=tag+' Teamantwort von Alice';
    await check('Teamchat: Bob sendet',async()=>{await go(bob,'/chat/1');await go(alice,'/chat/1');await bob.locator('#message').fill(tm1);await bob.locator('#chat-form button').click();await contains(bob,'.chat-content',tm1);});
    await check('Teamchat: Alice empfängt ohne Neuladen',async()=>{await contains(alice,'.chat-content',tm1,6000);});
    await check('Teamchat: Alice empfängt nach Neuladen und antwortet',async()=>{await go(alice,'/chat/1');await contains(alice,'.chat-content',tm1);await alice.locator('#message').fill(tm2);await alice.locator('#chat-form button').click();await contains(alice,'.chat-content',tm2);await go(bob,'/chat/1');await contains(bob,'.chat-content',tm2);await shot(bob,'teamchat-bob');await shot(alice,'teamchat-alice');});
    await check('Teamchat: leere Nachricht wird im Formular blockiert',async()=>{await bob.locator('#message').fill('');await bob.locator('#chat-form button').click();assert.equal(await bob.locator('#message').evaluate(e=>e.validity.valueMissing),true);});
    await check('Teamchat: KI-Frage liefert brauchbare Antwort',async()=>{await bob.locator('#ai-input').fill('Antworte mit einem kurzen Hallo.');await bob.locator('.ai-chat-row button').click();await bob.waitForFunction(()=>!['Noch keine Frage gestellt.','KI denkt ...'].includes(document.querySelector('#ai-answer').innerText));const text=await bob.locator('#ai-answer').innerText();assert.ok(!text.includes('Fehler'),text);return text;});
    await check('Teamchat: KI-Antwortvorschlag und Übernehmen',async()=>{await bob.getByRole('button',{name:'AI-Antwort vorschlagen'}).click();await bob.locator('.ai-suggestion-action').waitFor();const text=await bob.locator('#ai-suggestion').innerText();await bob.locator('.ai-suggestion-action').click();const value=await bob.locator('#message').inputValue();assert.ok(value.length>0);assert.ok(!value.includes('Fehler'),text);});
    await check('Chat: Zeitangabe entspricht Europe/Zurich',async()=>{const item=bob.locator('.chat-message').filter({hasText:tm2});const raw=await item.locator('[data-timestamp]').getAttribute('data-timestamp');const displayed=await item.locator('.chat-timestamp').innerText();const expected=await bob.evaluate(raw=>new Date(raw+'Z').toLocaleString('de-DE'),raw);assert.equal(displayed,expected,JSON.stringify({raw,displayed,expected}));});
  }
  if(phase==='workflows' || phase==='edgecases') await require('./'+phase+'.cjs')({bob,alice,actor,check,go,login,contains,shot,assert,tag,API,BASE,OUT,fs,path,browser,events});
  save();
  await browser.close();
}
main().catch(async e=>{console.error(e);save();if(browser)await browser.close();process.exitCode=1;});
