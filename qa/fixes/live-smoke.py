"""Read-only application checks; only test login tokens are created/revoked."""
import requests
from pathlib import Path
import json
base='http://127.0.0.1:3000'
results=[]
for name,password in [('bob','5678'),('alice','1234')]:
    s=requests.Session()
    response=s.post(base+'/login',json={'username':name,'password':password},timeout=10)
    assert response.status_code==200,(name,response.status_code)
    for path in ['/start','/users','/team/1','/chats','/chat/1','/chat/private/1/2']:
        response=s.get(base+path,timeout=10)
        assert response.status_code==200,(name,path,response.status_code)
    s.get(base+'/logout',timeout=10)
    assert not s.cookies.get('jwt_token')
    assert s.get(base+'/projects',allow_redirects=False,timeout=10).status_code==302
    results.append({'user':name,'status':'PASS'})
assert requests.get(base+'/chat/private/1/2',timeout=10).status_code==401
Path(__file__).with_name('live-result.json').write_text(json.dumps(results,indent=2))
print('Aktuelle Anwendung auf Port 3000: Bob und Alice, Dashboard, Benutzer, Team, beide Chats und Logout erfolgreich geprüft.')
