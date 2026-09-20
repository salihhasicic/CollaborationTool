module.exports=async function({bob,alice,actor,check,go,login,contains,shot,assert,tag,API,BASE,OUT,fs,path}) {
  const ids=JSON.parse(fs.readFileSync(path.join(OUT,'workflow-ids.json')));
  const fresh=await actor('neuregistrierung',{permissions:['geolocation'],geolocation:{latitude:47.3769,longitude:8.5417}});
  async function fillRegistration(name,photo=false) {
    await go(fresh,'/register');
    await fresh.waitForFunction(()=>document.querySelector('#latitude').value!=='');
    await fresh.locator('#username').fill(name);await fresh.locator('#password').fill('Test-5678!');
    await fresh.locator('#team_id').selectOption('1');await fresh.locator('#skills').fill('QA,Testing');await fresh.locator('#location').fill('Zürich');
    if(photo) await fresh.locator('#photo').setInputFiles({name:'qa.png',mimeType:'image/png',buffer:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=','base64')});
    const response=fresh.waitForResponse(r=>r.url().endsWith('/register')&&r.request().method()==='POST');
    await fresh.getByRole('button',{name:'Registrieren',exact:true}).click();return await response;
  }
  await check('Registrierung ohne Bild mit Standortfreigabe',async()=>{const r=await fillRegistration(tag);assert.equal(r.status(),200);await contains(fresh,'.message.success','erfolgreich');});
  await check('Neu registrierter Nutzer kann sich anmelden',async()=>{await login(fresh,tag,'Test-5678!');assert.ok((await fresh.locator('body').innerText()).includes(tag));});
  await check('Doppelte Registrierung zeigt verständliche Fehlermeldung',async()=>{await fillRegistration(tag);await contains(fresh,'.message.error','already exists');});
  await check('Registrierung mit Bild erzeugt keinen Serverfehler',async()=>{const r=await fillRegistration(tag+'-bild',true);assert.equal(r.status(),200,'Bildregistrierung: HTTP '+r.status());await contains(fresh,'.message.success','erfolgreich');});
  await check('Login mit falschem Passwort zeigt Fehler',async()=>{await go(fresh,'/logout');await fresh.locator('#username').fill('bob');await fresh.locator('#password').fill('falsch');await fresh.getByRole('button',{name:'Einloggen'}).click();await contains(fresh,'#error','falsch');assert.ok(fresh.url().endsWith('/login'));});
  await check('Login-Pflicht: Dashboard für ausgeloggte Sitzung gesperrt',async()=>{await go(fresh,'/start');assert.ok(fresh.url().endsWith('/login'));});
  await check('Logout: Projektinhalte verschwinden nach Abmelden',async()=>{await login(fresh,'bob','5678');await go(fresh,'/logout');await go(fresh,'/projects');assert.ok(!(await fresh.locator('body').innerText()).includes(ids.projectName),'Projektname bleibt nach Logout sichtbar');});
  await check('Logout: Projektänderungen sind nach Abmelden gesperrt',async()=>{await go(fresh,'/project/'+ids.projectId);const form=fresh.locator('#project_deadline');const exists=await form.count();assert.equal(exists,0,'Projektbearbeitung bleibt nach Logout erreichbar');});
  await check('Abgelaufener/ungültiger JWT: verständlicher Login statt Dashboard-500',async()=>{await login(fresh,'bob','5678');await fresh.context().addCookies([{name:'jwt_token',value:'invalid-qa-token',domain:'127.0.0.1',path:'/'}]);const r=await go(fresh,'/start');assert.notEqual(r.status(),500,'Dashboard stürzt mit ungültigem Token ab');assert.ok(fresh.url().includes('/login'));});
  await check('Navigationslinks: alle vorhandenen Menüpunkte erreichbar',async()=>{await go(bob,'/start');const links=await bob.locator('nav a:not([href="/logout"])').evaluateAll(es=>es.map(e=>e.getAttribute('href')));for(const href of links){const r=await go(bob,href);assert.equal(r.status(),200,href+' HTTP '+r.status());}return links;});
  await check('Profilübersicht: Demo-Profilbilder laden',async()=>{await go(bob,'/users');await bob.waitForTimeout(1200);const broken=await bob.locator('.user-card img').evaluateAll(es=>es.filter(e=>e.complete&&e.naturalWidth===0).map(e=>e.getAttribute('src')));assert.equal(broken.length,0,broken.length+' defekte Profilbilder');});
  await check('Privatchat: HTML-Nachricht wird im Nachrichtenbereich als Text dargestellt',async()=>{await go(bob,'/chats');await bob.locator('.chat-user-name').getByText('alice',{exact:true}).click();await bob.locator('#msgInput').fill('<b data-qa="markup">'+tag+'</b>');await bob.getByRole('button',{name:'Senden',exact:true}).click();await contains(bob,'.chat-msg-bubble','<b data-qa="markup">'+tag+'</b>');assert.equal(await bob.locator('#chat-messages [data-qa="markup"]').count(),0);});
  await check('Privatchat: HTML bleibt auch in der Vorschau Text',async()=>{await go(alice,'/chats');const injected=alice.locator('#last-msg-2 [data-qa="markup"]');assert.equal(await injected.count(),0,'HTML-Tag wird in der Chatvorschau als Element gerendert');});
  await check('Privatchat: gespeicherter JavaScript-Marker wird nicht ausgeführt',async()=>{await go(bob,'/chats');await bob.locator('.chat-user-name').getByText('alice',{exact:true}).click();await bob.locator('#msgInput').fill('<img src="/qa-missing-image" onerror="document.documentElement.dataset.qaXss=\'executed\'">');await bob.getByRole('button',{name:'Senden',exact:true}).click();await bob.waitForTimeout(300);await go(alice,'/chats');await alice.waitForTimeout(500);const marker=await alice.locator('html').getAttribute('data-qa-xss');await shot(alice,'chat-preview-injection');assert.equal(marker,null,'Gespeicherter Testcode wurde beim Empfänger ausgeführt');});
  // Replace the last preview with a harmless normal message after the proof.
  await bob.locator('#msgInput').fill(tag+' Ende des HTML-Tests');await bob.getByRole('button',{name:'Senden',exact:true}).click();
  const mobile=await actor('mobil',{viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
  await login(mobile,'bob','5678');
  const mobileRoutes=['/start','/users','/profile/2','/projects','/project/'+ids.projectId,'/chat/1','/chats','/team/1','/team_manage','/teams/new','/register','/login'];
  const mobileReport=[];
  for(const route of mobileRoutes){await go(mobile,route);const m=await mobile.evaluate(()=>({innerWidth,screenWidth:screen.width,scrollWidth:document.documentElement.scrollWidth,viewport:document.querySelector('meta[name=viewport]')?.content||null}));mobileReport.push({route,...m});await shot(mobile,'mobile-'+route.replaceAll('/','-'));}
  fs.writeFileSync(path.join(OUT,'mobile-layout.json'),JSON.stringify(mobileReport,null,2));
  await check('Mobile Ansicht nutzt Gerätebreite und vermeidet horizontales Scrollen',async()=>{const bad=mobileReport.filter(r=>r.innerWidth>400||r.scrollWidth>r.innerWidth+2);assert.equal(bad.length,0,JSON.stringify(bad));});
  await check('Mobile Ansicht: Login funktioniert',async()=>{await login(mobile,'bob','5678');assert.ok(mobile.url().endsWith('/start'));});
  await check('Desktop: große Ansichten ohne horizontalen Überlauf',async()=>{const report=[];for(const route of ['/start','/users','/projects','/project/'+ids.projectId,'/chats','/team/1']){await go(bob,route);report.push({route,...await bob.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth}))});}assert.ok(report.every(r=>r.scrollWidth<=r.width+2),JSON.stringify(report));return report;});
};
