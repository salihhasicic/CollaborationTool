import json,time,sqlite3,threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
API='http://127.0.0.1:5201'; WEB='http://127.0.0.1:3200'; ROOT=Path(__file__).parent
TAG=f'FIX-{time.time_ns()}'
results=[]
def test(name,fn):
 try:
  detail=fn();results.append({'name':name,'status':'PASS','detail':detail});print('PASS',name,detail,flush=True)
 except Exception as e:
  results.append({'name':name,'status':'FAIL','detail':str(e)});print('FAIL',name,str(e),flush=True)
 (ROOT/'results-reliability.json').write_text(json.dumps({'results':results},ensure_ascii=False,indent=2))
def login(name,pw):
 s=requests.Session();r=s.post(WEB+'/login',json={'username':name,'password':pw},timeout=10);r.raise_for_status();token=r.json()['access_token'];s.headers['Authorization']='Bearer '+token;return s,token
bob,bt=login('bob','5678');alice,at=login('alice','1234')
def concurrent():
 barrier=threading.Barrier(2)
 def send(who):
  token=bt if who==2 else at
  receiver=1 if who==2 else 2
  sent=[]
  for i in range(25):
   value=f'{TAG}-{who}-{i}';barrier.wait()
   r=requests.post(API+'/chat/private/send',json={'sender_id':who,'receiver_id':receiver,'content':value},headers={'Authorization':'Bearer '+token},timeout=10)
   assert r.status_code==200,(r.status_code,r.text)
   sent.append(value)
  return sent
 with ThreadPoolExecutor(max_workers=2) as pool:sent=sum(list(pool.map(send,[1,2])),[])
 messages=bob.get(API+'/chat/private/1/2',timeout=10).json()
 found=[m['content'] for m in messages if m['content'].startswith(TAG)]
 assert sorted(found)==sorted(sent),(len(sent),len(found))
 return {'sent':len(sent),'saved':len(found)}
test('50 gleichzeitige Chatnachrichten vollständig und genau einmal gespeichert',concurrent)
def spoof():
 r=bob.post(API+'/chat/private/send',json={'sender_id':1,'receiver_id':2,'content':TAG},timeout=10);assert r.status_code==403
 r=bob.post(API+'/chat/send',json={'sender_id':1,'team_id':1,'content':TAG},timeout=10);assert r.status_code==403
 return '403 für falsche Absender in beiden Chats'
test('Angemeldeter Nutzer kann keinen Absender vortäuschen',spoof)
def private():
 r=bob.get(API+'/chat/private/1/3',timeout=10);assert r.status_code==403
 r=bob.get(API+'/chat/team/2',timeout=10);assert r.status_code==403
 r=bob.post(API+'/user/update',json={'user_id':1,'skills':TAG},timeout=10);assert r.status_code==403
 return 'Fremdes Gespräch, Teamchat und Profiländerung gesperrt'
test('Eigentums- und Teamrechte',private)
def versions():
 paths=[]
 for payload in ['Version 1','Version 2']:
  r=bob.post(API+'/team/1/upload',files={'file':(TAG+'.txt',payload.encode(),'text/plain')},data={'uploader':'alice'},timeout=10)
  assert r.status_code==200,r.text
  paths.append(r.json()['storage_name'])
 assert paths[0]!=paths[1]
 for file,payload in zip(paths,['Version 1','Version 2']):assert bob.get(API+'/team/1/files/'+file,timeout=10).text==payload
 files=bob.get(API+'/team/1/files',timeout=10).json()['files'];items=[f for f in files if f['storage_name'] in paths]
 assert all(f['uploader']=='bob' for f in items)
 return 'Beide Versionen erhalten; Uploader aus verifizierter Identität'
test('Gleicher Dateiname erhält beide Inhalte und richtigen Uploader',versions)
def delete():
 r=bob.delete(API+'/team/1',timeout=10);assert r.status_code==409,r.text
 team=bob.post(API+'/team/create',json={'name':TAG},timeout=10).json()['team_id']
 assert alice.delete(API+f'/team/{team}',timeout=10).status_code==403
 assert bob.delete(API+f'/team/{team}',timeout=10).status_code==200
 return 'Befülltes Team blockiert; leeres Team nur durch Eigentümer gelöscht'
test('Löschregeln verhindern verwaiste Daten',delete)
def logout():
 bob.get(WEB+'/logout',timeout=10)
 assert bob.get(API+'/projects',timeout=10).status_code==401
 assert bob.get(WEB+'/projects',allow_redirects=False,timeout=10).status_code==302
 assert not bob.cookies.get('jwt_token')
 return 'Cookie entfernt; kopierter JWT ebenfalls widerrufen'
test('Logout widerruft auch kopierte Tokens',logout)
def csrf():
 r=alice.post(WEB+'/api/team/create',json={'name':TAG},headers={'Origin':'https://untrusted.example'},timeout=10);assert r.status_code==403
 return '403'
test('Browseranfragen fremder Herkunft abgelehnt',csrf)
