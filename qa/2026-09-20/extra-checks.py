import json,time,sqlite3,threading,os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
API='http://127.0.0.1:5101';WEB='http://127.0.0.1:3100';OUT=Path(__file__).parent
COPY=Path(os.environ.get('COLLAB_QA_COPY','/private/tmp/collab-qa-20260920'))
TAG=f'QA-EXTRA-{int(time.time())}'
results=[]
def check(name,fn):
 try:
  detail=fn();results.append({'name':name,'status':'PASS','detail':detail});print('PASS',name,detail,flush=True)
 except Exception as e:
  results.append({'name':name,'status':'FAIL','detail':str(e)});print('FAIL',name,str(e)[:250],flush=True)
 (OUT/'results-extra.json').write_text(json.dumps({'phase':'extra','results':results},indent=2,ensure_ascii=False))
def login(name,password):
 s=requests.Session();r=s.post(WEB+'/login',json={'username':name,'password':password},timeout=10);r.raise_for_status();s.headers['Authorization']='Bearer '+r.json()['access_token'];return s
bob=login('bob','5678');alice=login('alice','1234')
ids=json.loads((OUT/'workflow-ids.json').read_text());pid=ids['projectId']

def logout_write():
 bob.get(WEB+'/logout',timeout=5)
 r=bob.post(WEB+f'/project/{pid}/update_deadline',data={'deadline':'2026-12-24'},allow_redirects=False,timeout=5)
 actual=alice.get(API+f'/project/{pid}',timeout=5).json()['deadline']
 alice.patch(API+f'/project/{pid}/deadline',json={'deadline':None},timeout=5)
 assert actual!='2026-12-24T00:00:00',f'Projektdeadline nach Logout geändert; HTTP {r.status_code}, gespeichert {actual}'
check('Logout: tatsächliche Projektänderung muss gesperrt sein',logout_write)

def duplicate_file():
 filename=TAG+'.txt'
 for data in (b'Version 1',b'Version 2'):
  r=alice.post(API+'/team/1/upload',files={'file':(filename,data,'text/plain')},data={'uploader':'alice'},timeout=5);r.raise_for_status()
 rows=[x for x in alice.get(API+'/team/1/files',timeout=5).json()['files'] if x['filename']==filename]
 contents=alice.get(API+'/team/1/files/'+filename,timeout=5).text
 assert len(rows)==1,f'{len(rows)} Dateieinträge für denselben Namen; beide laden {contents!r}'
check('Dateiablage: gleicher Dateiname bleibt eindeutig',duplicate_file)

def populated_team():
 team=alice.post(API+'/team/create',json={'name':TAG},timeout=5).json()['team_id']
 username=TAG+'-user'
 r=alice.post(API+'/auth/register',data={'username':username,'password':'qa-pass','team_id':team,'latitude':'47.3','longitude':'8.5'},timeout=5);r.raise_for_status()
 s=login(username,'qa-pass')
 project=s.post(API+'/project',json={'name':TAG+' Projekt','team_id':team},timeout=5).json()['id']
 s.post(API+f'/project/{project}/task',json={'title':TAG+' Task'},timeout=5).raise_for_status()
 r=alice.delete(API+f'/team/{team}',timeout=5)
 with sqlite3.connect(f'file:{COPY}/backend/instance/collab.db?mode=ro',uri=True) as db:
  orphaned=db.execute('select count(*) from project p left join team t on p.team_id=t.id where t.id is null').fetchone()[0]
 assert r.status_code in (400,409) or orphaned==0,f'HTTP {r.status_code}; {orphaned} Projekt(e) ohne zugehöriges Team nach Löschen'
check('Team mit Mitgliedern und Projekt löschen: keine verwaisten Daten',populated_team)

def parallel_chat():
 # Snapshot only the disposable copy and restore it, including if concurrency corrupts JSON.
 private_file=COPY/'backend/private_messages.json';before=private_file.read_bytes()
 responses=[];sent=[]
 try:
  with ThreadPoolExecutor(max_workers=2) as pool:
   for round_no in range(10):
    barrier=threading.Barrier(2)
    def send(sender,receiver):
     marker=f'{TAG}-parallel-{round_no}-{sender}';barrier.wait()
     r=requests.post(API+'/chat/private/send',json={'sender_id':sender,'receiver_id':receiver,'content':marker},timeout=5)
     return marker,r.status_code
    pair=list(pool.map(lambda pair:send(*pair),[(1,2),(2,1)]))
    sent.extend(marker for marker,_ in pair);responses.extend(code for _,code in pair)
  data=requests.get(API+'/chat/private/1/2',timeout=5)
  if data.status_code!=200:raise AssertionError(f'Nach 20 gleichzeitigen Nachrichten ist Verlauf nicht lesbar: HTTP {data.status_code}; Sendestatus {responses}')
  received={m['content'] for m in data.json()}
  missing=[m for m in sent if m not in received]
  assert not missing and all(s==200 for s in responses),f'{len(sent)} gesendet, {len(sent)-len(missing)} gespeichert; fehlend {missing}; HTTP-Status {responses}'
  return {'sent':len(sent),'saved':len(sent)-len(missing)}
 finally:
  private_file.write_bytes(before)
check('Bob und Alice senden gleichzeitig: alle 20 Nachrichten bleiben erhalten',parallel_chat)
