import json,hashlib
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
COPY=Path('/private/tmp/collab-qa-20260920')
phases=['pages-chat','workflows','edgecases','api','extra']
rows=[]
for phase in phases:
 d=json.loads((OUT/f'results-{phase}.json').read_text())
 for i,r in enumerate(d['results']):
  if phase in ('workflows','edgecases') and i<2:continue
  if phase=='workflows' and i in (3,4):continue
  rows.append({'id':f'{phase}-{i+1:02d}','phase':phase,**r})
counts=Counter(x['status'] for x in rows)
(OUT/'results-consolidated.json').write_text(json.dumps({'total':len(rows),'counts':dict(counts),'results':rows},ensure_ascii=False,indent=2))
files=[ROOT/'main.py',*ROOT.glob('backend/*.py'),*ROOT.glob('backend/routes/*.py'),*ROOT.glob('templates/*.html'),*ROOT.glob('static/*.css')]
manifest=[]
for source in files:
 rel=source.relative_to(ROOT);target=COPY/rel
 manifest.append({'path':str(rel),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'test_copy_identical':target.exists() and source.read_bytes()==target.read_bytes()})
(OUT/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
assert all(x['test_copy_identical'] for x in manifest)
def src(name,line):return f'[{name}:{line}]({ROOT/name}:{line})'
text=f'''# Funktionstest SYNQ / Collaboration Tool

Getestet am 20.09.2026. **Die Anwendung funktioniert teilweise, aber nicht vollständig.** Mehrere Kernabläufe funktionieren. Es bestehen reproduzierte Fehler bei Chat, Registrierung, Logout, Teamnotizen und Team-Erstellung sowie erhebliche Lücken bei der Zugriffskontrolle.

**{len(rows)} ausgewertete Prüfungen: {counts['PASS']} bestanden, {counts['FAIL']} mit Fehler oder Einschränkung.** Das sind einzelne Prüfungen, nicht ebenso viele unterschiedliche Bugs. Mehrere Prüfungen betreffen dieselbe Ursache. Wiederholte Login-Vorbereitung und zwei Folgeprüfungen nach einer gescheiterten Registrierung wurden aus dieser Zählung entfernt. Registrierung ohne Bild, neuer Login und Duplikatprüfung wurden anschließend unabhängig erfolgreich geprüft.

## Testaufbau und Aussagekraft

- Tatsächliche Bedienung in Google Chrome mit Playwright; Bob und Alice hatten getrennte Browserkontexte mit unabhängigem Login und getrennten Cookies. Zusätzlich Carla und eigens registrierte Testnutzer.
- Desktop: 1440 × 1000; mobile Emulation: 390 × 844, Touch, Zeitzone Europe/Zurich. Die mobile Emulation ersetzt keinen Test auf einem echten Telefon.
- Isolierte Projektkopie unter `/private/tmp/collab-qa-20260920`; Webserver `http://127.0.0.1:3100`, Backend `http://127.0.0.1:5101`. Datenbank, Nachrichten und Uploads wurden vor den Tests kopiert. Alle Testmutationen betrafen diese Kopie.
- Der geprüfte Python-, Template- und CSS-Code stimmt mit dem Arbeitsprojekt überein: [Dateiprüfsummen](source-manifest.json). Am Anwendungscode wurden während dieses Audits keine Fehlerbehebungen vorgenommen.
- Alle 16 über Routen verwendeten Seitenvorlagen wurden im Browser besucht und ihre angebotenen Funktionen getestet. `templates/index.html` ist nicht eingebunden: `/` leitet auf `/login` weiter. Die zwei privaten Chatansichten wurden getrennt getestet.
- Zusätzlich wurden API-Antworten, ungültige Eingaben, Gastzugriffe, fremde Teams, Logout, gespeichertes HTML und gleichzeitige Chatnachrichten geprüft. Eine erfolgreiche HTTP-200-Seite allein wurde nicht als funktionierender Ablauf gewertet.
- KI-Erzeugung ist ohne konfigurierten API-Schlüssel nicht erfolgreich testbar. Die aktuelle Fehlerbehandlung wurde getestet. Karten und Browser-Standortfreigabe wurden mit fest vorgegebenen Testkoordinaten geprüft.
- Kein vollständiger Lasttest und keine Tests in Safari/Firefox, auf echten Mobilgeräten oder einer öffentlichen Deployment-Umgebung. Es wird keine Fehlerfreiheit außerhalb der dokumentierten Fälle behauptet.

## Seiten und Funktionen

| Seite / Bereich | Erfolgreich geprüft | Fehler / Einschränkungen |
|---|---|---|
| `/`, `/login` | Weiterleitung; Bob/Alice getrennt anmelden; falsches Passwort; Pflichtfelder; mobiler Login | Backend-Login mit fehlenden JSON-Feldern gibt 500 statt Eingabefehler zurück |
| `/register` | Registrierung ohne Bild mit Standort; anschließender Login; doppelte Namen; ungültige Bilddaten im API | Mit Bild: 500; ohne Standortkoordinaten: 500 im Backend und generische Fehlermeldung im Formular |
| `/start` | Dashboard leer und mit Daten; übernommene Tasks; Fortschrittsanzeige bis 100 % | Ungültiger JWT führt zu 500; mobile Darstellung |
| `/users` | Skill-Suche, keine Treffer, Profil-/Teamlinks, Umkreissuche | 19 Demo-Profilbilder defekt; kein sinnvoller Ersatz für nicht ladende Bilder |
| `/profile/<id>` | Eigenes/fremdes Profil; Standort, Skills, Geolocation, Karte; Bild hochladen und nach Reload anzeigen | Privatchat-Schaltfläche führt in defekte Chatansicht; Profil-API erlaubt Änderungen ohne Login |
| `/projects` | Projektliste; Projekt für Bob und Alice sichtbar; Statusspalten | Projekte bleiben nach Logout lesbar |
| `/projects/new` | Projekt mit Deadline erstellen | Unvollständiger Logout erlaubt weitere Projektnutzung; API-Validierung lückenhaft |
| `/project/<id>` | Aufgaben, Projektdeadline setzen und entfernen | Projektname fehlt; Teamname fehlt; unbekannte ID wird als 500 ausgegeben |
| `/project/<id>/tasks/new` | Aufgabe mit Beschreibung, Sonderzeichen und Deadline erstellen | API akzeptiert leere Titel |
| `/tasks/new` | Projekt wählen und Aufgabe anlegen | Fehlerbehandlung bei ungültigen Daten lückenhaft |
| Aufgabenaktionen | Als Bob übernehmen; Alice sieht Zuweisung; Doppelübernahme abgelehnt; Status und Deadline ändern/entfernen; Projektstatus wird nachgeführt | API erlaubt Alice die Änderung einer Bob zugewiesenen Aufgabe, obwohl die UI das nicht anbietet; beliebige Statuswerte akzeptiert |
| `/team/<id>` | Mitglieder ansehen, hinzufügen/verschieben; Teamauswahl; Upload; Download mit identischem Inhalt | Notizen werden nicht gespeichert; Uploader „unbekannt“; gleicher Dateiname erzeugt doppelte Einträge und überschreibt Inhalt |
| `/team_manage` | Teams anzeigen; Team erstellen; leeres Testteam löschen | Löschen eines Teams mit Projekt lässt verwaiste Projektdaten zurück; Backend-Löschen ohne Anmeldung möglich |
| `/teams/new` | Seite/Formular vorhanden | Erstellen funktioniert nicht; falscher API-Pfad |
| `/chats` | Bob → Alice und Alice → Bob; Umlaute/Emoji; Speicherung; Verlauf nach erneutem Öffnen | Keine automatische Aktualisierung; Vorschau führt eingeschleustes HTML/JavaScript aus; paralleles Senden verliert Nachrichten |
| `/private_chat/<id>` | Seite öffnet sich | Verlauf lädt nicht; Senden liefert 500 |
| `/chat/<team_id>` | Teamnachrichten in beide Richtungen; nach Reload sichtbar; leere Formulareingabe blockiert | Kein automatisches Nachladen; falsche lokale Uhrzeit; KI derzeit nicht nutzbar |
| `/logout` | Loginseite erscheint; Dashboard wird über Sitzungsprüfung gesperrt | JWT bleibt gültig im Browser: Projektinhalte weiterhin lesbar und Projektdeadline tatsächlich nach Logout änderbar |

## Bob und Alice: tatsächlicher Chat-Test

1. Bob und Alice in zwei unabhängigen Browserkontexten angemeldet.
2. In beiden `/chats` geöffnet und jeweils den anderen Nutzer ausgewählt.
3. Bob sendet eine markierte Nachricht mit `äöü 🙂`. Bob sieht sie sofort. Alice sieht sie **nicht automatisch**, aber nach erneutem Öffnen des Gesprächs.
4. Alice antwortet. Bob sieht die Antwort nach erneutem Öffnen. Beide Nachrichten bleiben nach einem Reload erhalten.
5. Dasselbe im Teamchat geprüft: Senden und Persistenz funktionieren, Empfang erfordert ebenfalls Reload.
6. Einstieg über fremdes Profil → „Privater Chat“ scheitert: `/chat/private/null/1` liefert 404, Senden liefert 500.
7. Zusätzlicher Gleichzeitigkeitstest: zehn Runden mit jeweils einer Nachricht von Bob und Alice, also **20 Sendungen**. Alle Anfragen wurden mit HTTP 200 bestätigt, im Verlauf standen aber nur **17 Nachrichten**. Drei Nachrichten gingen verloren. Die Nachrichten-Datei der Testkopie wurde nach diesem Test auf ihren vorherigen Zustand zurückgesetzt.

Belege: [Bobs Chat](screenshots/chat-bob.png), [Alices Chat](screenshots/chat-alice.png), [Teamchat Bob](screenshots/teamchat-bob.png), [Teamchat Alice](screenshots/teamchat-alice.png), [Messwerte gleichzeitiges Senden](results-extra.json).

## Befunde nach Priorität

### P0 – Zugriffsschutz und Datenzuverlässigkeit

**F01 – Viele APIs prüfen Anmeldung und Berechtigung nicht.**

Ohne Cookie und ohne Bearer-Token lieferten private und Teamchat-Leseanfragen HTTP 200. Nachrichten konnten mit frei gesetzter `sender_id` im Namen von Alice/Bob gesendet werden. Ebenso wurden Änderungen an Profilen, Teamzuordnungen und Notizen sowie das Löschen eines eigens angelegten Testteams ohne Anmeldung akzeptiert. Die Teamdateiliste war offen. Der Web-Proxy für private Nachrichten ist ebenfalls ungeschützt.

Reproduktion: in einer nicht angemeldeten Sitzung beispielsweise `GET /chat/private/1/2` am Backend aufrufen. Erwartet: 401/403; tatsächlich: Nachrichteninhalt. Die ausführbaren Tests dokumentieren auch die Änderungen an Testdaten.

Ursachen: {src('backend/routes/private_chat_routes.py',21)}, {src('backend/routes/chat_routes.py',9)}, {src('backend/routes/user_routes.py',27)}, {src('backend/routes/team_routes.py',49)}. Senderidentität sollte aus der verifizierten Sitzung stammen; Team- und Gesprächszugehörigkeit müssen serverseitig geprüft werden.

**F02 – Gespeichertes JavaScript in der Chatvorschau.**

Eine Nachricht mit einem harmlosen HTML-Testmarker wurde im Nachrichtenbereich korrekt als Text angezeigt. Nach Neuladen von Alices Chatübersicht wurde dieselbe Nachricht in der Vorschau als HTML verarbeitet. Ein isolierter `onerror`-Test setzte beim Empfänger das DOM-Attribut `data-qa-xss="executed"`. Es wurden keine Daten ausgelesen oder nach außen übertragen.

Ursache: ungefiltertes `last.content` in `innerHTML`, {src('templates/chats.html',264)}. Dieselbe Escape-Behandlung wie im Nachrichtenbereich bzw. `textContent` verwenden.

**F03 – Gleichzeitige private Nachrichten gehen verloren.**

20 Sendungen, 20 Erfolgsantworten, nur 17 gespeicherte Nachrichten. Der Dateiablauf liest den gesamten JSON-Verlauf, ergänzt lokal und überschreibt die Datei ohne Transaktion/Sperre. Zwei gleichzeitige Schreibvorgänge können sich gegenseitig überschreiben. Ursache: {src('backend/routes/private_chat_routes.py',17)} und {src('backend/routes/private_chat_routes.py',33)}. Nachrichten sollten transaktional in der Datenbank gespeichert werden.

### P1 – Anmeldung und Kernfunktionen

**F04 – Logout meldet nur teilweise ab.**

Nach Logout waren Projektname und Projektformular weiter erreichbar. Eine tatsächliche Deadline-Änderung auf `2026-12-24` wurde gespeichert. Die Teständerung wurde anschließend zurückgesetzt. Ursache: {src('main.py',73)} löscht nur `session['user_id']`; JWT-Cookie und Browser-Token bleiben bestehen, mehrere Projektrouten verlassen sich nur auf das Cookie.

**F05 – Privatchat aus Profil funktioniert nicht.**

Der Login speichert nur `access_token`, während diese Ansicht `localStorage.user_id` benötigt. Ergebnis: `null` im Lese-Endpunkt und 500 beim Senden. Ursache: {src('templates/private_chat.html',141)} gegenüber {src('templates/login.html',162)}. Die bestätigte Benutzer-ID sollte konsistent aus der Sitzung an das Template übergeben werden.

**F06 – Registrierung mit Bild: HTTP 500.**

Im Formular gültiges PNG auswählen, Namen/Passwort/Team/Ort ausfüllen, Standort erlauben, absenden. Der Frontend-Server scheitert beim Weiterreichen der Datei an Requests: `TypeError: a bytes-like object is required, not 'FileStorage'`. Ohne Bild funktioniert die Registrierung. Ursache: {src('main.py',235)} und {src('main.py',252)}; Datei mit Dateiname, Stream und MIME-Typ weitergeben.

**F07 – Registrierung ohne Standortfreigabe scheitert.**

Koordinaten bleiben leere Strings; diese werden an Float-Spalten übergeben. Der Backend-Aufruf liefert 500, die Oberfläche nur „Registrierung fehlgeschlagen.“. Ursache: {src('backend/routes/auth_routes.py',20)} und {src('backend/routes/auth_routes.py',58)}. Leere optionale Koordinaten in `None` umwandeln und ungültige Werte kontrolliert ablehnen.

**F08 – Teamnotizen werden nicht gespeichert.**

Bob schreibt eine Notiz und klickt Speichern; nach Neuladen oder bei Alice fehlt sie. Frontend sendet Formulardaten, Backend liest zunächst `request.json`. Flask antwortet daher 415, bevor `request.form` erreicht wird. Der Frontend-Ablauf ignoriert den Fehler. JSON-Anfragen direkt an denselben Endpunkt funktionieren. Ursache: {src('backend/routes/team_routes.py',72)} und {src('main.py',99)}.

**F09 – Separate Team-Erstellung defekt.**

`/teams/new` → Teamname → „Team erstellen“ führt zu „Netzwerkfehler.“. Die Seite sendet an `/team`; vorhanden ist `/team/create`. Erstellen über `/team_manage` funktioniert. Ursache: {src('templates/create_team.html',41)}. Außerdem erwartet die Erfolgsausgabe `data.name`, das die aktuelle API nicht zurückgibt.

**F10 – Team löschen lässt Projekte ohne Team zurück.**

In einem eigens erstellten Team mit Mitglied, Projekt und Task wurde das Team mit HTTP 200 gelöscht. Danach blieb ein Projekt mit nicht mehr vorhandener Team-ID in der Datenbank. Ursache: {src('backend/routes/team_routes.py',117)}. Vorhandene abhängige Daten benötigen eine definierte Lösch-/Verschieberegel oder eine Ablehnung des Löschens.

**F11 – Fehlender/ungültiger JWT verursacht Dashboard-500.**

Bei bestehender Flask-Sitzung das JWT-Cookie durch einen ungültigen Testwert ersetzen und `/start` öffnen. Statt Loginaufforderung folgt 500. `progress_projects` wird nur im Erfolgszweig der Projektabfrage initialisiert, später aber immer verwendet: {src('main.py',548)} und {src('main.py',562)}.

### P2 – Verhalten, Validierung und Darstellung

**F12 – Beide Chatübersichten laden neue Nachrichten nicht automatisch.** Gegenstelle mindestens sechs Sekunden offen gelassen; neue Inhalte erscheinen erst durch erneutes Öffnen bzw. Reload. Es fehlen Polling oder eine Push-Verbindung. Das ist eine funktionale Einschränkung, unabhängig vom Verlustproblem F03.

**F13 – Chatzeiten sind zwei Stunden zu früh.** Beispiel: UTC-Zeit `10:22:37` wurde im Browser mit Europe/Zurich als `10:22:37` statt `12:22:37` angezeigt. Zeitstempel enthalten keine Zeitzonenkennung. Ursache: `datetime.utcnow().isoformat()` und lokale Interpretation durch JavaScript, unter anderem {src('templates/chat.html',402)}.

**F14 – Datei-Uploader steht auf „unbekannt“.** Trotz Bob-Login liest der Upload `localStorage.user_id`, das beim Login nicht gesetzt wird. Ursache: {src('templates/team.html',317)}. Upload/Download selbst funktionieren.

**F15 – Gleiche Dateinamen überschreiben den Inhalt und erzeugen doppelte Einträge.** Zwei Uploads desselben Namens erzeugten zwei Metadateneinträge; beide Downloads lieferten nur Version 2. Ursache: {src('backend/routes/team_routes.py',92)}. Eindeutige Speicher-IDs oder bewusstes Versionieren/Ersetzen notwendig.

**F16 – Eingabeprüfung fehlt an mehreren APIs.** Fehlende Login-Felder und ungültige Datumswerte erzeugen 500. Leere Tasktitel, reine Leerzeichen als Teamname und beliebige Projekt-/Taskstatus werden akzeptiert. Unbekannte Statuswerte verschwinden aus den drei vorgesehenen Kanban-Spalten. Die Prüfungen enthalten sowohl erwartete Ablehnung als auch tatsächlich erhaltenen HTTP-Status.

**F17 – Aufgabenrechte sind inkonsistent.** Alice kann per API den Status einer Bob zugewiesenen Aufgabe ändern, obwohl die UI Änderungen nur dem Verantwortlichen anbietet. Carla aus einem anderen Team kann Bobs Aufgabenliste abfragen. Projekt-Lesen/-Ändern und Task-Übernahme über die normalen Projektendpunkte wurden dagegen korrekt mit 403 gesperrt. Ursachen: {src('backend/routes/project_routes.py',116)} und {src('backend/routes/project_routes.py',152)}.

**F18 – Projekt-Details zeigen Namen nicht vollständig.** Die Seite zeigt nur „Tasks für Projekt #…“, nicht den Projektnamen. Der Teamname fehlt ebenfalls, weil `GET /team/<id>` nicht implementiert ist und 405 liefert. Eine unbekannte Projekt-ID wird im Frontend als 500 statt 404 angezeigt. Beleg: [Projekt mit Tasks](screenshots/project-with-tasks.png).

**F19 – Mobile Darstellung ist nicht an die Gerätebreite angepasst.** Auf allen zwölf geprüften mobilen Routen fehlt die Viewport-Angabe. Bei 390 Pixel Gerätebreite layoutet der Browser auf 980 Pixel und verkleinert die Seite; im Chat überdeckt die Navigation zusätzlich Inhalt. Login funktioniert auch mobil. Beleg: [mobiler Chat](screenshots/mobile--chats.png), [Messwerte](mobile-layout.json).

**F20 – Demo-Profilbilder defekt.** 19 Bilder in der Benutzerübersicht luden nicht; Demo-Datensätze verweisen auf `https://example.com/photo.jpg`. Hochgeladene echte Profilbilder funktionierten. Es fehlt ein Fallback, wenn eine vorhandene URL nicht lädt.

**F21 – KI ist aktuell nicht konfiguriert; Fehler wird als Antwort angeboten.** Ohne API-Schlüssel erscheinen technische OpenAI-Fehlermeldungen sowohl im KI-Chat als auch im Antwortvorschlag. Der Vorschlag kann sogar über „Übernehmen“ ins Nachrichtenfeld kopiert werden. {src('backend/utils.py',22)} fängt den Fehler ab und gibt ihn als normalen Antworttext zurück. Ein positiver KI-Test bleibt bis zur Konfiguration offen.

## Sinnvolle Reihenfolge für die Behebung

1. Zugriffskontrolle, Chatvorschau-Escaping, vollständiges Logout und transaktionale Chat-Speicherung.
2. Defekter Profil-Privatchat, Registrierung, Teamnotizen, Team-Erstellung und Löschregeln.
3. Automatische Chataktualisierung, Validierungen, Zeitstempel, Dateimetadaten und Fehlerbehandlung.
4. Mobile Darstellung, Demo-Bilder, Projektbeschriftung und KI-Konfiguration.

## Prüfprotokoll und Reproduktion

- [Einzelprüfungen mit Ergebnis](TESTFAELLE.md)
- [Konsolidiertes JSON](results-consolidated.json)
- [Seiteninventar mit Formularen und Links](page-inventory.json)
- [Browser-Testprogramm](browser-audit.cjs), [Formularabläufe](workflows.cjs), [Grenzfälle](edgecases.cjs)
- [API-Testprogramm](api-audit.py), [Gleichzeitigkeit und Datenkonsistenz](extra-checks.py)
- [Wiederholung und Testkopie](REPRODUKTION.md)

Die Fehler sind dokumentiert und wurden während dieses Audits nicht im Anwendungscode behoben. Die ursprünglichen Server und Arbeitsdaten wurden für die Testmutationen nicht verwendet.
'''
(OUT/'BERICHT.md').write_text(text)
lines=['# Einzelprüfungen','',f'{len(rows)} ausgewertete Prüfungen: {counts["PASS"]} bestanden, {counts["FAIL"]} mit Fehler/Einschränkung.','', 'Die zwei Folgeprüfungen nach der fehlgeschlagenen Bildregistrierung wurden ausgeschlossen; spätere unabhängige Registrierungstests sind enthalten. PASS bedeutet nur, dass der benannte Fall bestanden wurde.','', '| ID | Prüfung | Ergebnis | Beobachtung |','|---|---|---|---|']
for r in rows:
 detail=r.get('detail','')
 if not isinstance(detail,str):detail=json.dumps(detail,ensure_ascii=False)
 detail=detail.replace('\n',' ').replace('|',' / ').replace('<','&lt;').replace('>','&gt;')[:550]
 lines.append(f'| {r["id"]} | {r["name"]} | {"OK" if r["status"]=="PASS" else "FEHLER / EINSCHRÄNKUNG"} | {detail or "Erwartetes Verhalten bestätigt."} |')
(OUT/'TESTFAELLE.md').write_text('\n'.join(lines)+'\n')
print({'tests':len(rows),'counts':dict(counts),'identical_source_files':len(manifest)})
