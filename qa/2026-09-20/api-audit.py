"""Integration checks against the isolated QA copy; never against the working database."""
import json
import time
from pathlib import Path
import requests

BASE='http://127.0.0.1:3100'
API='http://127.0.0.1:5101'
OUT=Path(__file__).parent
TAG=f'QA-API-{int(time.time())}'
results=[]
sessions={name:requests.Session() for name in ('bob','alice','carla','guest')}
for name,password in [('bob','5678'),('alice','1234'),('carla','pass123')]:
    r=sessions[name].post(BASE+'/login',json={'username':name,'password':password},timeout=10)
    r.raise_for_status()
    sessions[name].headers['Authorization']='Bearer '+r.json()['access_token']

def req(who,method,path,**kwargs):
    return sessions[who].request(method,(BASE if kwargs.pop('web',False) else API)+path,timeout=10,**kwargs)

def test(name,fn):
    try:
        detail=fn()
        results.append({'name':name,'status':'PASS','detail':detail})
        print('PASS',name,flush=True)
    except Exception as e:
        results.append({'name':name,'status':'FAIL','detail':str(e)})
        print('FAIL',name,str(e)[:180],flush=True)
    (OUT/'results-api.json').write_text(json.dumps({'phase':'api','tag':TAG,'results':results},ensure_ascii=False,indent=2))

def status(r,expected):
    assert r.status_code in expected, f'HTTP {r.status_code}, erwartet {expected}; Antwort: {r.text[:180]}'
    return {'http':r.status_code}

def deny(r):return status(r,(401,403))

project=req('bob','POST','/project',json={'name':TAG,'team_id':1}).json()
pid=project['id']
task=req('bob','POST',f'/project/{pid}/task',json={'title':TAG+' Task'}).json()
tid=task['id']
req('bob','POST',f'/task/{tid}/assign')

test('Login: falsches Passwort',lambda:status(req('guest','POST','/auth/login',json={'username':'bob','password':'falsch'}),(401,)))
test('Login: unbekannter Nutzer',lambda:status(req('guest','POST','/auth/login',json={'username':TAG,'password':'falsch'}),(401,)))
test('Login: fehlende Felder verursachen keinen Serverfehler',lambda:status(req('guest','POST','/auth/login',json={}),(400,401,422)))
test('Registrierung ohne Koordinaten',lambda:status(req('guest','POST','/auth/register',data={'username':TAG+'-no-geo','password':'qa-pass','team_id':1,'location':'Bern','latitude':'','longitude':''}),(201,)))
test('Registrierung mit Koordinaten',lambda:status(req('guest','POST','/auth/register',data={'username':TAG+'-valid','password':'qa-pass','team_id':1,'location':'Bern','latitude':'46.9481','longitude':'7.4474'}),(201,)))
test('Registrierung: Duplikat abgelehnt',lambda:status(req('guest','POST','/auth/register',data={'username':TAG+'-valid','password':'qa-pass','team_id':1,'latitude':'46.9481','longitude':'7.4474'}),(400,)))
test('Registrierung: ungültige Bilddatei abgelehnt',lambda:status(req('guest','POST','/auth/register',data={'username':TAG+'-bad-photo','password':'qa-pass','team_id':1},files={'photo':('qa.txt',b'keine Bilddaten','text/plain')}),(400,)))
test('Projekte ohne Login gesperrt',lambda:deny(req('guest','GET','/projects')))
test('Fremdes Team: Carla kann Projekt nicht lesen',lambda:deny(req('carla','GET',f'/project/{pid}')))
test('Fremdes Team: Carla kann Projekt nicht verändern',lambda:deny(req('carla','PATCH',f'/project/{pid}/deadline',json={'deadline':'2026-12-01'})))
test('Fremdes Team: Carla kann Task nicht übernehmen',lambda:deny(req('carla','POST',f'/task/{tid}/assign')))
test('Übernommener Task kann nicht doppelt übernommen werden',lambda:status(req('alice','POST',f'/task/{tid}/assign'),(400,409)))
test('Nur Task-Verantwortlicher darf Status ändern (wie UI)',lambda:deny(req('alice','PATCH',f'/task/{tid}/status',json={'status':'In Progress'})))
test('Task: ungültiger Status wird abgelehnt',lambda:status(req('bob','PATCH',f'/task/{tid}/status',json={'status':'ungueltig'}),(400,422)))
req('bob','PATCH',f'/task/{tid}/status',json={'status':'To Do'})
test('Projekt: ungültiger Status wird abgelehnt',lambda:status(req('bob','PATCH',f'/project/{pid}/status',json={'status':'ungueltig'}),(400,422)))
req('bob','PATCH',f'/project/{pid}/status',json={'status':'To Do'})
test('Task: ungültiges Datum verursacht keinen Serverfehler',lambda:status(req('bob','PATCH',f'/task/{tid}/deadline',json={'deadline':'kein-datum'}),(400,422)))
test('Projekt: ungültiges Datum verursacht keinen Serverfehler',lambda:status(req('bob','PATCH',f'/project/{pid}/deadline',json={'deadline':'2026-99-99'}),(400,422)))
test('Task: leerer Titel wird abgelehnt',lambda:status(req('bob','POST',f'/project/{pid}/task',json={'title':''}),(400,422)))
test('Nicht vorhandenes Projekt liefert 404 im Backend',lambda:status(req('bob','GET','/project/999999'),(404,)))
test('Nicht vorhandenes Projekt liefert 404 in Oberfläche',lambda:status(req('bob','GET','/project/999999',web=True),(404,)))
test('Team-Detail-Endpunkt für Teamname vorhanden',lambda:status(req('bob','GET','/team/1'),(200,)))
test('Teamnotizen akzeptieren Formularanfrage',lambda:status(req('bob','POST','/team/1/ablage',data={'ablage':TAG}),(200,)))
test('Teamnotizen akzeptieren JSON',lambda:status(req('bob','POST','/team/1/ablage',json={'ablage':TAG}),(200,)))

# Access checks only modify disposable records or write explicitly marked test messages.
test('Gast darf privaten Chat nicht lesen',lambda:deny(req('guest','GET','/chat/private/1/2')))
test('Gast darf keinen Absender im privaten Chat vortäuschen',lambda:deny(req('guest','POST','/chat/private/send',json={'sender_id':1,'receiver_id':2,'content':TAG+' Gast als Alice'})))
test('Web-Proxy schützt private Nachrichten vor Gästen',lambda:deny(req('guest','POST','/chat/private/send',web=True,json={'sender_id':2,'receiver_id':1,'content':TAG+' Gast via Proxy'})))
test('Gast darf Teamchat nicht lesen',lambda:deny(req('guest','GET','/chat/team/1')))
test('Gast darf Teamnachricht nicht als Bob senden',lambda:deny(req('guest','POST','/chat/send',json={'sender_id':2,'team_id':1,'content':TAG+' Gast als Bob'})))
test('Privatchat lehnt leere Nachrichten ab',lambda:status(req('bob','POST','/chat/private/send',json={'sender_id':2,'receiver_id':1,'content':'   '}),(400,422)))
test('Teamchat lehnt leere Nachrichten ab',lambda:status(req('bob','POST','/chat/send',json={'sender_id':2,'team_id':1,'content':''}),(400,422)))
test('Fremdes Team: Carla darf Bob-Aufgaben nicht auslesen',lambda:deny(req('carla','GET','/user/2/tasks')))
test('Gast darf Profil nicht verändern',lambda:deny(req('guest','POST','/user/update',json={'user_id':3,'skills':'Java,Spring'})))
test('Gast darf Teamzuordnung nicht ändern',lambda:deny(req('guest','POST','/team/join',json={'user_id':3,'team_id':2})))
test('Gast darf Teamnotizen nicht ändern',lambda:deny(req('guest','POST','/team/1/ablage',json={'ablage':TAG+' Gastnotiz'})))
test('Gast darf Teamdateien nicht lesen',lambda:deny(req('guest','GET','/team/1/files')))
team=req('bob','POST','/team/create',json={'name':TAG+' delete'}).json()['team_id']
test('Gast darf Team nicht löschen',lambda:deny(req('guest','DELETE',f'/team/{team}')))
test('Teamname darf nicht nur Leerzeichen enthalten',lambda:status(req('bob','POST','/team/create',json={'name':'   '}),(400,422)))
test('Umkreissuche benötigt Login',lambda:deny(req('guest','GET','/user/nearby')))
test('Logout entfernt Zugriff auf Projektliste',lambda:(req('bob','GET','/logout',web=True),status(req('bob','GET','/projects',web=True,allow_redirects=False),(302,401,403)))[1])
print(json.dumps({'total':len(results),'pass':sum(r['status']=='PASS' for r in results),'fail':sum(r['status']=='FAIL' for r in results)}))
