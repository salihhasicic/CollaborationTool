"""Non-destructive, one-time migration of existing JSON messages and uploads."""
import json
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import inspect, text
from extensions import db


def parse_date(value):
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.tzinfo:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def migrate(app):
    with app.app_context():
        db.create_all()
        with db.engine.connect() as connection:
            connection.exec_driver_sql('BEGIN IMMEDIATE')
            try:
                columns = {c['name'] for c in inspect(connection).get_columns('team')}
                if 'owner_id' not in columns:
                    connection.exec_driver_sql('ALTER TABLE team ADD COLUMN owner_id INTEGER')
                connection.exec_driver_sql('UPDATE team SET owner_id = (SELECT MIN(id) FROM user WHERE user.team_id = team.id) WHERE owner_id IS NULL')
                marker = connection.execute(text("SELECT key FROM schema_migration WHERE key = 'json_to_database_v1'")).first()
                if not marker:
                    from models import PrivateMessage, TeamFile
                    base = Path(app.root_path)
                    messages = base / 'private_messages.json'
                    # Historical IDs only belong to a pre-existing user database.
                    # Never attach bundled legacy conversations to newly registered accounts.
                    has_existing_users = connection.execute(text('SELECT COUNT(*) FROM user')).scalar() > 0
                    if messages.exists() and has_existing_users:
                        for row in json.loads(messages.read_text()):
                            connection.execute(PrivateMessage.__table__.insert().values(
                                sender_id=int(row['sender_id']), receiver_id=int(row['receiver_id']),
                                content=row['content'], timestamp=parse_date(row['timestamp'])))
                    metadata_files = (base / 'uploads').glob('team_*_files.json') if has_existing_users else ()
                    for metadata in metadata_files:
                        team_id = int(metadata.name.split('_')[1])
                        seen = set()
                        for row in json.loads(metadata.read_text()):
                            if row['filename'] in seen:
                                continue
                            seen.add(row['filename'])
                            connection.execute(TeamFile.__table__.insert().values(
                                team_id=team_id, filename=row['filename'], storage_name=row['filename'],
                                uploader=row.get('uploader') or 'unbekannt', uploaded_at=parse_date(row['uploaded_at'])))
                    connection.execute(text("INSERT INTO schema_migration (key) VALUES ('json_to_database_v1')"))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
