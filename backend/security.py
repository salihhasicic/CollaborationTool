"""Validation and authorization shared by API routes."""
from datetime import datetime, timezone
import math
import os
import secrets
from pathlib import Path
from flask import abort, g, request, current_app
from extensions import db
from models import Team


def persistent_secret(directory, name, environment):
    configured = os.environ.get(environment)
    if configured:
        return configured
    path = Path(directory) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('x') as file:
            os.chmod(path, 0o600)
            file.write(secrets.token_hex(32))
    except FileExistsError:
        pass
    return path.read_text().strip()


def data():
    value = request.get_json(silent=True)
    if not isinstance(value, dict):
        abort(400, description='Bitte gültige JSON-Daten senden.')
    return value


def text(value, label, limit=10000, required=False):
    if not isinstance(value, str):
        abort(400, description=f'{label} muss Text sein.')
    value = value.strip()
    if (required and not value) or len(value) > limit:
        abort(400, description=f'{label} fehlt oder ist zu lang (maximal {limit} Zeichen).')
    return value


def integer(value, label='ID'):
    try:
        if isinstance(value, bool) or str(int(value)) != str(value):
            raise ValueError
        result = int(value)
        if result < 1:
            raise ValueError
        return result
    except (ValueError, TypeError):
        abort(400, description=f'{label} ist ungültig.')


def coordinate(value, limit):
    if value in (None, ''):
        return None
    try:
        result = float(value)
        if not math.isfinite(result) or not -limit <= result <= limit:
            raise ValueError
        return result
    except (ValueError, TypeError):
        abort(400, description='Ungültige Standortkoordinaten.')


def deadline(value):
    if value in (None, ''):
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError):
        abort(400, description='Bitte ein gültiges Datum im Format JJJJ-MM-TT angeben.')


def status(value):
    if value not in ('To Do', 'In Progress', 'Done'):
        abort(400, description='Ungültiger Status.')
    return value


def own_user(value):
    if value is not None and integer(value) != g.user.id:
        abort(403, description='Du kannst nur dein eigenes Profil ändern.')
    return g.user


def team_access(team_id):
    team = db.get_or_404(Team, team_id)
    if g.user.team_id != team.id and team.owner_id != g.user.id:
        abort(403, description='Du gehörst diesem Team nicht an.')
    return team


def utc_iso(value):
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def save_photo(file):
    import imghdr
    import uuid
    if not file or not file.filename:
        abort(400, description='Bitte ein Bild auswählen.')
    header = file.read(512)
    file.seek(0)
    kind = imghdr.what(None, header)
    if kind not in ('png', 'jpeg', 'gif', 'webp'):
        abort(400, description='Bitte ein PNG-, JPEG-, GIF- oder WebP-Bild auswählen.')
    directory = Path(current_app.root_path).parent / 'static' / 'photos'
    directory.mkdir(parents=True, exist_ok=True)
    filename = f'{uuid.uuid4().hex}.{kind}'
    file.save(directory / filename)
    return f'/static/photos/{filename}'
