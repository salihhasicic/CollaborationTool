# Fehlerbehebungen und Nachprüfung

Die im Audit gefundenen Codefehler sind behoben. **132 Browser- und API-Prüfungen bestanden, kein fehlgeschlagener Fall.** Wiederholte Login-Vorbereitungen wurden nicht doppelt gezählt. Zusätzlich bestanden zwei gezielte Frontend-Tests, zwei Migrationstests, die Prüfung der wiederholbaren Datenmigration und die Kontrolle der laufenden Anwendung mit Bob und Alice.

Die KI-Fehlerbehandlung ist korrigiert. **Echte KI-Antworten bleiben bis zur Einrichtung von `OPENAI_API_KEY` ungetestet und nicht verfügbar.** Der Test prüft hier die verständliche Konfigurationsmeldung und dass kein Fehlertext als Antwort übernommen werden kann.

| Audit-Befund | Umsetzung / Nachweis |
|---|---|
| F01: offene APIs | Zentrale JWT-Prüfung; Gesprächsteilnahme, Teamzugehörigkeit und eigene Profiländerungen serverseitig geprüft. Browserzugriffe laufen über einen geschützten Proxy auf derselben Origin. |
| F02: Chatvorschau führt HTML aus | Chattexte und Namen werden als Textknoten eingefügt. Der frühere JavaScript-Testmarker wird beim Empfänger nicht ausgeführt. |
| F03: verlorene Nachrichten | Private Nachrichten liegen in SQLite statt einer gemeinsam überschriebenen JSON-Datei. 50 gleichzeitig gesendete Nachrichten wurden vollständig und genau einmal gespeichert. |
| F04: unvollständiges Logout | Sitzung und Cookie werden entfernt; JWT wird serverseitig widerrufen. Auch eine zuvor kopierte Token-Version wird danach abgelehnt. |
| F05: defekter Privatchat aus Profil | Benutzer-ID kommt aus der bestätigten Sitzung. Lesen und Senden funktionieren über beide Chatansichten. |
| F06: Registrierung mit Bild | Korrekte Weitergabe von Dateiname, Stream und MIME-Typ. Bildregistrierung und anschließender Login im Browser bestanden. |
| F07: Registrierung ohne Standort | Leere Koordinaten werden als fehlend gespeichert, ungültige Werte kontrolliert abgelehnt. Registrierung ohne Freigabe bestanden. |
| F08: Teamnotizen | Formular und JSON werden korrekt verarbeitet; Änderungen erscheinen auch bei Alice. Backend-Fehler werden nicht mehr verschluckt. |
| F09: separate Team-Erstellung | Einheitlicher Endpunkt und passende Antwortfelder; beide Erstellungswege bestanden. |
| F10: verwaiste Projekte beim Teamlöschen | Teams mit Mitgliedern, Projekten, Nachrichten, Dateien oder Notizen werden mit einer verständlichen Meldung vor dem Löschen geschützt. Leere Teams können Berechtigte löschen. |
| F11: Dashboard bei ungültigem JWT | Ungültige/abgelaufene Sitzung führt zum Login; keine uninitialisierten Dashboard-Variablen. |
| F12: kein automatischer Chatempfang | Beide Chats laden alle 1,5 Sekunden neue Nachrichten nach; Formular und Eingabefeld bleiben dabei erhalten. |
| F13: falsche Uhrzeit | API-Zeitstempel enthalten UTC-Zeitzone; Browser zeigt Europe/Zurich korrekt an. |
| F14: unbekannter Uploader | Identität kommt aus dem verifizierten Konto; gefälschte Uploader-Angaben werden ignoriert. |
| F15: Überschreiben gleicher Dateinamen | Jeder Upload bekommt eine eigene Speicher-ID. Gleiche Anzeigenamen bleiben als getrennte Versionen herunterladbar; beide Inhalte geprüft. |
| F16: fehlende Validierung | Namen, IDs, Textlängen, Koordinaten, Statuswerte und Datumswerte werden validiert. Fehler liefern passende 4xx-Antworten statt 500. |
| F17: inkonsistente Aufgabenrechte | Nur Verantwortliche ändern zugewiesene Tasks; Doppelübernahme wird atomar verhindert; fremde persönliche Aufgabenlisten sind gesperrt. |
| F18: Projekt-/Teamnamen und Fehlerseiten | Beide Namen sichtbar; Team-Detail-Endpunkt vorhanden; unbekanntes Projekt liefert 404. |
| F19: mobile Darstellung | Viewport und schmale Layouts ergänzt; zwölf mobile Seiten sowie Desktop geprüft. |
| F20: defekte Avatare | Lokaler Standardavatar und Ladefehler-Fallback; echte Profilbilder bleiben erhalten. |
| F21: technische KI-Fehler als Vorschlag | Verständliche Fehlermeldung, keine Übernahme-Schaltfläche für Fehler; API-Schlüssel weiterhin erforderlich. |

## Daten und Berechtigungen

Vor der Migration wurde die Datenbank unter `backend/instance/before-audit-fixes/collab.db` gesichert. Die bisherige JSON-Datei bleibt erhalten. Alle 22 historischen privaten Nachrichten wurden in die Datenbank übernommen. Ein wiederholter Start importiert sie nicht erneut. Vorhandene Dateimetadaten wurden ebenfalls übernommen; bestehende Dateien bleiben herunterladbar.

Die laufende Datenbank enthält weiterhin dieselben 20 Nutzer, 3 Teams sowie unveränderte Anzahlen vorhandener Projekte, Tasks und Teamnachrichten. Die Testmutationen wurden auf einer separaten Kopie ausgeführt.

Teamdaten sind für Mitglieder und die Person zugänglich, die das Team erstellt hat. Bei bestehenden Teams wurde das erste vorhandene Mitglied als Eigentümer eingetragen. Die Benutzerübersicht und private Gespräche bleiben für angemeldete Nutzer verfügbar. Die öffentliche Registrierung kann die Teamnamen zur Auswahl laden; dabei werden keine Teamdateien, Notizen oder Nachrichten freigegeben.

Lokale Sitzungs- und JWT-Schlüssel werden einmalig zufällig erzeugt und unter den ignorierten `instance`-Verzeichnissen gespeichert. Die bisherigen fest codierten Schlüssel werden nicht mehr verwendet. Deshalb nach dem Update neu einloggen.

## Nachweise

- [Konsolidierte Prüfergebnisse](results-consolidated.json)
- [API-Prüfungen](results-api.json)
- [Chat, Dateien, Logout und gleichzeitiges Senden](results-reliability.json)
- [Migrationsprüfung](migration-result.json)
- [Laufende Anwendung: Bob und Alice](live-result.json)
- [Mobiler Chat](screenshots/mobile--chats.png)
- [Mobile Projektseite](screenshots/mobile--project-2.png)
- [Projekt mit Aufgaben](screenshots/project-with-tasks.png)

Browserprüfungen: Google Chrome, Desktop 1440 × 1000 und mobile Emulation 390 × 844. Andere Browser, echte Mobilgeräte und ein öffentlicher Server wurden nicht getestet.

## Tests wiederholen

Die Programme in diesem Ordner verwenden ausschließlich die isolierten Ports 3200/5201. `live-smoke.py` prüft ausdrücklich die laufende Anwendung auf 3000 und ändert keine Inhaltsdaten.

Die Testkopie liegt unter `/private/tmp/collab-fixes-20260920`. Mit dem Python der Projekt-`.venv` läuft dort `serve.py`. Nach Start des Testservers aus dem Projektverzeichnis:

```sh
node qa/fixes/browser-audit.cjs pages-chat
node qa/fixes/browser-audit.cjs workflows
node qa/fixes/browser-audit.cjs edgecases
.venv/bin/python qa/fixes/api-audit.py
.venv/bin/python qa/fixes/reliability.py
.venv/bin/python qa/fixes/test_frontend.py
.venv/bin/python qa/fixes/test_migrations.py
```

Für eine frische Testkopie das Kopierskript aus `qa/2026-09-20/prepare-test-copy.py` mit einem neuen Ziel verwenden und in dessen `serve.py` die Testports von 3100/5101 auf 3200/5201 setzen. Testdateien und Screenshots werden bei einem weiteren Lauf überschrieben. Die Programme protokollieren fehlgeschlagene Einzelprüfungen und laufen dann weiter; entscheidend sind die Ergebnisdateien, nicht nur der Prozess-Exitcode.
