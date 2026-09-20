import json
import sys
import tempfile
import unittest
from pathlib import Path
from flask import Flask
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'backend'))
from extensions import db
from models import User, PrivateMessage, TeamFile
from migrations import migrate

class MigrationTests(unittest.TestCase):
    def fixture(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root=Path(directory.name)
        history=[{'sender_id':1,'receiver_id':2,'content':'Historische Nachricht','timestamp':'2025-07-02T12:00:00'}]
        (root/'private_messages.json').write_text(json.dumps(history))
        (root/'uploads').mkdir()
        (root/'uploads/team_1_files.json').write_text(json.dumps([{'filename':'legacy.txt','uploader':'alice','uploaded_at':'2025-07-02T12:00:00'}]))
        app=Flask('migration_test',root_path=str(root))
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite://'
        db.init_app(app)
        return app

    def add_users(self):
        db.session.add_all([User(id=1,username='alice',password='test'),User(id=2,username='bob',password='test')])
        db.session.commit()

    def test_existing_history_imported_once(self):
        app=self.fixture()
        with app.app_context():
            db.create_all()
            self.add_users()
            migrate(app)
            migrate(app)
            self.assertEqual(PrivateMessage.query.count(),1)
            self.assertEqual(TeamFile.query.count(),1)
            self.assertEqual(PrivateMessage.query.first().content,'Historische Nachricht')

    def test_fresh_database_never_attaches_old_ids_to_new_accounts(self):
        app=self.fixture()
        with app.app_context():
            migrate(app)
            self.add_users()
            migrate(app)
            self.assertEqual(PrivateMessage.query.count(),0)
            self.assertEqual(TeamFile.query.count(),0)

if __name__=='__main__':unittest.main()
