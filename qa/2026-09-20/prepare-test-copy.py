"""Create an isolated audit copy without touching the working database."""
import shutil
import sqlite3
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[2]
dest=Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/collab-qa-repeat').resolve()
if dest.exists():
    raise SystemExit(f'Ziel existiert bereits: {dest}. Bitte einen neuen, leeren Pfad wählen.')
if dest==root or root in dest.parents:
    raise SystemExit('Bitte ein Ziel außerhalb des Arbeitsprojekts wählen.')
dest.mkdir(parents=True)
for name in ('backend','templates','static'):
    shutil.copytree(root/name,dest/name,ignore=shutil.ignore_patterns('__pycache__','instance'))
shutil.copy2(root/'main.py',dest/'main.py')
(dest/'backend/instance').mkdir()
with sqlite3.connect(f'file:{root}/backend/instance/collab.db?mode=ro',uri=True) as source, sqlite3.connect(dest/'backend/instance/collab.db') as target:
    source.backup(target)
(dest/'serve.py').write_text('''import os,sys,threading
from werkzeug.serving import make_server
os.environ['BACKEND_URL']='http://127.0.0.1:5101'
sys.path.insert(0,os.path.join(os.path.dirname(__file__),'backend'))
from app import app as backend
from main import app as frontend
api=make_server('127.0.0.1',5101,backend,threaded=True)
web=make_server('127.0.0.1',3100,frontend,threaded=True)
threading.Thread(target=api.serve_forever,daemon=True).start()
print('Testkopie: http://127.0.0.1:3100',flush=True)
try:
    web.serve_forever()
finally:
    api.shutdown()
''')
print(dest)
