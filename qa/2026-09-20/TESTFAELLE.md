# Einzelprüfungen

128 ausgewertete Prüfungen: 76 bestanden, 52 mit Fehler/Einschränkung.

Die zwei Folgeprüfungen nach der fehlgeschlagenen Bildregistrierung wurden ausgeschlossen; spätere unabhängige Registrierungstests sind enthalten. PASS bedeutet nur, dass der benannte Fall bestanden wurde.

| ID | Prüfung | Ergebnis | Beobachtung |
|---|---|---|---|
| pages-chat-01 | Login Bob über Formular | OK | {"url": "http://127.0.0.1:3100/start"} |
| pages-chat-02 | Login Alice in unabhängiger Sitzung | OK | {"url": "http://127.0.0.1:3100/start"} |
| pages-chat-03 | Seite /start | OK | {"title": "Dashboard – bob", "forms": 0} |
| pages-chat-04 | Seite /projects | OK | {"title": "Projekte des Teams 1", "forms": 0} |
| pages-chat-05 | Seite /projects/new | OK | {"title": "Projekt anlegen", "forms": 1} |
| pages-chat-06 | Seite /tasks/new | OK | {"title": "Neuen Task erstellen", "forms": 1} |
| pages-chat-07 | Seite /users | OK | {"title": "Benutzerübersicht", "forms": 1} |
| pages-chat-08 | Seite /profile/2 | OK | {"title": "Profil", "forms": 0} |
| pages-chat-09 | Seite /profile/1 | OK | {"title": "Profil", "forms": 0} |
| pages-chat-10 | Seite /team/1 | OK | {"title": "Team 1", "forms": 4} |
| pages-chat-11 | Seite /team/2 | OK | {"title": "Team 2", "forms": 4} |
| pages-chat-12 | Seite /team_manage | OK | {"title": "Team verwalten", "forms": 4} |
| pages-chat-13 | Seite /teams/new | OK | {"title": "Neues Team erstellen", "forms": 1} |
| pages-chat-14 | Seite /chat/1 | OK | {"title": "Team Chat 1", "forms": 1} |
| pages-chat-15 | Seite /chats | OK | {"title": "Private Chats", "forms": 0} |
| pages-chat-16 | Seite /private_chat/1 | OK | {"title": "Privater Chat", "forms": 1} |
| pages-chat-17 | Seite /register | OK | {"title": "Registrieren", "forms": 1} |
| pages-chat-18 | Seite /login | OK | {"title": "Login", "forms": 1} |
| pages-chat-19 | Privatchat /chats: Bob sendet Alice | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-20 | Privatchat: Alice empfängt ohne Neuladen | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 6000ms exceeded. Call log: [2m  - waiting for locator('.chat-msg-bubble').filter({ hasText: 'QA-1789899721827 Bob → Alice äöü 🙂' }).first() to be visible[22m  |
| pages-chat-21 | Privatchat: Alice empfängt nach erneutem Öffnen | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-22 | Privatchat: Alice antwortet Bob | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-23 | Privatchat: Nachrichten bleiben nach Neuladen erhalten | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-24 | Privatchat aus fremdem Profil öffnen und Verlauf laden | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 5000ms exceeded. Call log: [2m  - waiting for locator('#messages').filter({ hasText: 'QA-1789899721827 Bob → Alice äöü 🙂' }).first() to be visible[22m  |
| pages-chat-25 | Privatchat aus Profil: Senden funktioniert | FEHLER / EINSCHRÄNKUNG | Senden liefert HTTP 500  500 !== 200  |
| pages-chat-26 | Teamchat: Bob sendet | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-27 | Teamchat: Alice empfängt ohne Neuladen | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 6000ms exceeded. Call log: [2m  - waiting for locator('.chat-content').filter({ hasText: 'QA-1789899721827 Teamnachricht von Bob' }).first() to be visible[22m  |
| pages-chat-28 | Teamchat: Alice empfängt nach Neuladen und antwortet | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-29 | Teamchat: leere Nachricht wird im Formular blockiert | OK | Erwartetes Verhalten bestätigt. |
| pages-chat-30 | Teamchat: KI-Frage liefert brauchbare Antwort | FEHLER / EINSCHRÄNKUNG | [Fehler bei GPT: No API key provided. You can set your API key in code using 'openai.api_key = ', or you can set the environment variable OPENAI_API_KEY=). If your API key is stored in a file, you can point the openai module at it with 'openai.api_key_path = '. You can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details.] |
| pages-chat-31 | Teamchat: KI-Antwortvorschlag und Übernehmen | FEHLER / EINSCHRÄNKUNG | [Fehler bei GPT: No API key provided. You can set your API key in code using 'openai.api_key = ', or you can set the environment variable OPENAI_API_KEY=). If your API key is stored in a file, you can point the openai module at it with 'openai.api_key_path = '. You can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details.] Übernehmen |
| pages-chat-32 | Chat: Zeitangabe entspricht Europe/Zurich | FEHLER / EINSCHRÄNKUNG | {"raw":"2026-09-20T10:22:37.320885","displayed":"20.9.2026, 10:22:37","expected":"20.9.2026, 12:22:37"} + actual - expected  + '20.9.2026, 10:22:37' - '20.9.2026, 12:22:37'                ^  |
| workflows-03 | Registrierung: Standort erlaubt, mit Profilbild | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 5000ms exceeded. Call log: [2m  - waiting for locator('.message.success').filter({ hasText: 'erfolgreich' }).first() to be visible[22m  |
| workflows-06 | Registrierung: ohne Standortfreigabe möglich | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 5000ms exceeded. Call log: [2m  - waiting for locator('.message.success').filter({ hasText: 'erfolgreich' }).first() to be visible[22m  |
| workflows-07 | Benutzersuche nach Skill Python | OK | {"anzahl": 2} |
| workflows-08 | Benutzersuche: keine Treffer | OK | Erwartetes Verhalten bestätigt. |
| workflows-09 | Umkreissuche Bob | OK | Nutzer im Umkreis: ivan (25.9 km) lisa (25.26 km) paula (26.81 km) qa-register-repro (0 km) |
| workflows-10 | Profilkarte lädt | OK | {"tiles": 10} |
| workflows-11 | Profil: Ort und Skills speichern und erneut laden | OK | Erwartetes Verhalten bestätigt. |
| workflows-12 | Profil: aktuellen Standort übernehmen | OK | Erwartetes Verhalten bestätigt. |
| workflows-13 | Profil: Bild hochladen und nach Neuladen anzeigen | OK | Erwartetes Verhalten bestätigt. |
| workflows-14 | Fremdes Profil zeigt keine Bearbeiten-Schaltfläche | OK | Erwartetes Verhalten bestätigt. |
| workflows-15 | Projekt über Formular erstellen | OK | {"projectId": 2} |
| workflows-16 | Projekt ist für Alice sichtbar | OK | Erwartetes Verhalten bestätigt. |
| workflows-17 | Projekt: Name ist auf Detailseite sichtbar | FEHLER / EINSCHRÄNKUNG | Projektname fehlt auf Detailseite |
| workflows-18 | Projekt: Teamname ist auf Detailseite sichtbar | FEHLER / EINSCHRÄNKUNG | Teamname fehlt auf Detailseite |
| workflows-19 | Projekt: Deadline ändern | OK | Erwartetes Verhalten bestätigt. |
| workflows-20 | Projekt: Deadline entfernen | OK | Erwartetes Verhalten bestätigt. |
| workflows-21 | Task über Projekt erstellen | OK | {"taskId": 1} |
| workflows-22 | Task übernehmen als Bob | OK | Erwartetes Verhalten bestätigt. |
| workflows-23 | Alice sieht Bobs Task als zugewiesen | OK | Erwartetes Verhalten bestätigt. |
| workflows-24 | Task: Status In Progress und Projektstatus | OK | Erwartetes Verhalten bestätigt. |
| workflows-25 | Task: Deadline ändern | OK | Erwartetes Verhalten bestätigt. |
| workflows-26 | Task: Deadline entfernen | OK | Erwartetes Verhalten bestätigt. |
| workflows-27 | Dashboard zeigt übernommene offene Aufgabe | OK | Erwartetes Verhalten bestätigt. |
| workflows-28 | Task: Done und 100 Prozent Projektfortschritt | OK | Erwartetes Verhalten bestätigt. |
| workflows-29 | Allgemeines Task-Formular erstellt zweite Aufgabe | OK | Erwartetes Verhalten bestätigt. |
| workflows-30 | Teamnotiz speichern und bei Alice sichtbar | FEHLER / EINSCHRÄNKUNG | Expected values to be strictly equal: + actual - expected  + '' - 'QA-1789899822472 Notiz'  |
| workflows-31 | Teamdatei hochladen und bei Alice anzeigen | OK | Erwartetes Verhalten bestätigt. |
| workflows-32 | Teamdatei nennt tatsächlichen Uploader Bob | FEHLER / EINSCHRÄNKUNG | QA-1789899822472-upload.txt Hochgeladen von unbekannt am 20.9.2026, 10:24:28 |
| workflows-33 | Teamdatei herunterladen: Inhalt stimmt | OK | Erwartetes Verhalten bestätigt. |
| workflows-34 | Team: Mitglied hinzufügen | OK | Erwartetes Verhalten bestätigt. |
| workflows-35 | Team: Mitglied zurück ins ursprüngliche Team verschieben | OK | Erwartetes Verhalten bestätigt. |
| workflows-36 | Team-Auswahl wechselt die angezeigte Seite | OK | Erwartetes Verhalten bestätigt. |
| workflows-37 | Teamverwaltung zeigt die Teamnamen | OK | Erwartetes Verhalten bestätigt. |
| workflows-38 | Team über Teamverwaltung erstellen | OK | {"teamId": 4} |
| workflows-39 | Team über separate Seite /teams/new erstellen | FEHLER / EINSCHRÄNKUNG | locator.waitFor: Timeout 5000ms exceeded. Call log: [2m  - waiting for locator('#team-create-status').filter({ hasText: 'erfolgreich' }).first() to be visible[22m  |
| workflows-40 | Leeres Testteam über Oberfläche löschen | OK | Erwartetes Verhalten bestätigt. |
| edgecases-03 | Registrierung ohne Bild mit Standortfreigabe | OK | Erwartetes Verhalten bestätigt. |
| edgecases-04 | Neu registrierter Nutzer kann sich anmelden | OK | Erwartetes Verhalten bestätigt. |
| edgecases-05 | Doppelte Registrierung zeigt verständliche Fehlermeldung | OK | Erwartetes Verhalten bestätigt. |
| edgecases-06 | Registrierung mit Bild erzeugt keinen Serverfehler | FEHLER / EINSCHRÄNKUNG | Bildregistrierung: HTTP 500  500 !== 200  |
| edgecases-07 | Login mit falschem Passwort zeigt Fehler | OK | Erwartetes Verhalten bestätigt. |
| edgecases-08 | Login-Pflicht: Dashboard für ausgeloggte Sitzung gesperrt | OK | Erwartetes Verhalten bestätigt. |
| edgecases-09 | Logout: Projektinhalte verschwinden nach Abmelden | FEHLER / EINSCHRÄNKUNG | Projektname bleibt nach Logout sichtbar |
| edgecases-10 | Logout: Projektänderungen sind nach Abmelden gesperrt | FEHLER / EINSCHRÄNKUNG | Projektbearbeitung bleibt nach Logout erreichbar  1 !== 0  |
| edgecases-11 | Abgelaufener/ungültiger JWT: verständlicher Login statt Dashboard-500 | FEHLER / EINSCHRÄNKUNG | Dashboard stürzt mit ungültigem Token ab |
| edgecases-12 | Navigationslinks: alle vorhandenen Menüpunkte erreichbar | OK | ["/start", "/projects", "/users", "/chats", "/team/1", "/chat/1", "/team_manage", "/profile/2"] |
| edgecases-13 | Profilübersicht: Demo-Profilbilder laden | FEHLER / EINSCHRÄNKUNG | 19 defekte Profilbilder  19 !== 0  |
| edgecases-14 | Privatchat: HTML-Nachricht wird im Nachrichtenbereich als Text dargestellt | OK | Erwartetes Verhalten bestätigt. |
| edgecases-15 | Privatchat: HTML bleibt auch in der Vorschau Text | FEHLER / EINSCHRÄNKUNG | HTML-Tag wird in der Chatvorschau als Element gerendert  1 !== 0  |
| edgecases-16 | Privatchat: gespeicherter JavaScript-Marker wird nicht ausgeführt | FEHLER / EINSCHRÄNKUNG | Gespeicherter Testcode wurde beim Empfänger ausgeführt  'executed' !== null  |
| edgecases-17 | Mobile Ansicht nutzt Gerätebreite und vermeidet horizontales Scrollen | FEHLER / EINSCHRÄNKUNG | [{"route":"/start","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route":"/users","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route":"/profile/2","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route":"/projects","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route":"/project/2","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route":"/chat/1","innerWidth":980,"screenWidth":390,"scrollWidth":980,"viewport":null},{"route": |
| edgecases-18 | Mobile Ansicht: Login funktioniert | OK | Erwartetes Verhalten bestätigt. |
| edgecases-19 | Desktop: große Ansichten ohne horizontalen Überlauf | OK | [{"route": "/start", "width": 1440, "scrollWidth": 1440}, {"route": "/users", "width": 1440, "scrollWidth": 1440}, {"route": "/projects", "width": 1440, "scrollWidth": 1440}, {"route": "/project/2", "width": 1440, "scrollWidth": 1440}, {"route": "/chats", "width": 1440, "scrollWidth": 1440}, {"route": "/team/1", "width": 1440, "scrollWidth": 1440}] |
| api-01 | Login: falsches Passwort | OK | {"http": 401} |
| api-02 | Login: unbekannter Nutzer | OK | {"http": 401} |
| api-03 | Login: fehlende Felder verursachen keinen Serverfehler | FEHLER / EINSCHRÄNKUNG | HTTP 500, erwartet (400, 401, 422); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;500 Internal Server Error&lt;/title&gt; &lt;h1&gt;Internal Server Error&lt;/h1&gt; &lt;p&gt;The server encountered an internal error and was unable to complete your r |
| api-04 | Registrierung ohne Koordinaten | FEHLER / EINSCHRÄNKUNG | HTTP 500, erwartet (201,); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;500 Internal Server Error&lt;/title&gt; &lt;h1&gt;Internal Server Error&lt;/h1&gt; &lt;p&gt;The server encountered an internal error and was unable to complete your r |
| api-05 | Registrierung mit Koordinaten | OK | {"http": 201} |
| api-06 | Registrierung: Duplikat abgelehnt | OK | {"http": 400} |
| api-07 | Registrierung: ungültige Bilddatei abgelehnt | OK | {"http": 400} |
| api-08 | Projekte ohne Login gesperrt | OK | {"http": 401} |
| api-09 | Fremdes Team: Carla kann Projekt nicht lesen | OK | {"http": 403} |
| api-10 | Fremdes Team: Carla kann Projekt nicht verändern | OK | {"http": 403} |
| api-11 | Fremdes Team: Carla kann Task nicht übernehmen | OK | {"http": 403} |
| api-12 | Übernommener Task kann nicht doppelt übernommen werden | OK | {"http": 400} |
| api-13 | Nur Task-Verantwortlicher darf Status ändern (wie UI) | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"id":3,"project_status":"In Progress","status":"In Progress"}  |
| api-14 | Task: ungültiger Status wird abgelehnt | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (400, 422); Antwort: {"id":3,"project_status":"In Progress","status":"ungueltig"}  |
| api-15 | Projekt: ungültiger Status wird abgelehnt | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (400, 422); Antwort: {"id":3,"status":"ungueltig"}  |
| api-16 | Task: ungültiges Datum verursacht keinen Serverfehler | FEHLER / EINSCHRÄNKUNG | HTTP 500, erwartet (400, 422); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;500 Internal Server Error&lt;/title&gt; &lt;h1&gt;Internal Server Error&lt;/h1&gt; &lt;p&gt;The server encountered an internal error and was unable to complete your r |
| api-17 | Projekt: ungültiges Datum verursacht keinen Serverfehler | FEHLER / EINSCHRÄNKUNG | HTTP 500, erwartet (400, 422); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;500 Internal Server Error&lt;/title&gt; &lt;h1&gt;Internal Server Error&lt;/h1&gt; &lt;p&gt;The server encountered an internal error and was unable to complete your r |
| api-18 | Task: leerer Titel wird abgelehnt | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (400, 422); Antwort: {"id":4,"project_id":3,"project_status":"To Do","status":"To Do","title":""}  |
| api-19 | Nicht vorhandenes Projekt liefert 404 im Backend | OK | {"http": 404} |
| api-20 | Nicht vorhandenes Projekt liefert 404 in Oberfläche | FEHLER / EINSCHRÄNKUNG | HTTP 500, erwartet (404,); Antwort: Fehler beim Laden der Tasks (Status: 404): &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;404 Not Found&lt;/title&gt; &lt;h1&gt;Not Found&lt;/h1&gt; &lt;p&gt;The requested URL was not found on the server. If you e |
| api-21 | Team-Detail-Endpunkt für Teamname vorhanden | FEHLER / EINSCHRÄNKUNG | HTTP 405, erwartet (200,); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;405 Method Not Allowed&lt;/title&gt; &lt;h1&gt;Method Not Allowed&lt;/h1&gt; &lt;p&gt;The method is not allowed for the requested URL.&lt;/p&gt;  |
| api-22 | Teamnotizen akzeptieren Formularanfrage | FEHLER / EINSCHRÄNKUNG | HTTP 415, erwartet (200,); Antwort: &lt;!doctype html&gt; &lt;html lang=en&gt; &lt;title&gt;415 Unsupported Media Type&lt;/title&gt; &lt;h1&gt;Unsupported Media Type&lt;/h1&gt; &lt;p&gt;Did not attempt to load JSON data because the request Content-Type was n |
| api-23 | Teamnotizen akzeptieren JSON | OK | {"http": 200} |
| api-24 | Gast darf privaten Chat nicht lesen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: [{"content":"Hallo von Postman!","receiver_id":2,"receiver_name":"bob","sender_id":1,"sender_name":"alice","timestamp":"2025-07-02T06:16:00.561838"},{"content":"hihi","receiver_id" |
| api-25 | Gast darf keinen Absender im privaten Chat vortäuschen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"Nachricht gesendet."}  |
| api-26 | Web-Proxy schützt private Nachrichten vor Gästen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"Nachricht gesendet."}  |
| api-27 | Gast darf Teamchat nicht lesen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: [{"content":"QA-1789899539675 Teamnachricht von Bob","sender_id":2,"sender_name":"bob","timestamp":"2026-09-20T10:19:45.504365"},{"content":"QA-1789899539675 Teamantwort von Alice" |
| api-28 | Gast darf Teamnachricht nicht als Bob senden | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"Message sent"}  |
| api-29 | Privatchat lehnt leere Nachrichten ab | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (400, 422); Antwort: {"message":"Nachricht gesendet."}  |
| api-30 | Teamchat lehnt leere Nachrichten ab | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (400, 422); Antwort: {"message":"Message sent"}  |
| api-31 | Fremdes Team: Carla darf Bob-Aufgaben nicht auslesen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: [{"deadline":null,"id":1,"project_id":2,"status":"Done","title":"QA-1789899822472 Aufgabe"},{"deadline":null,"id":3,"project_id":3,"status":"To Do","title":"QA-API-1789899923 Task" |
| api-32 | Gast darf Profil nicht verändern | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"User updated"}  |
| api-33 | Gast darf Teamzuordnung nicht ändern | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"User added to team"}  |
| api-34 | Gast darf Teamnotizen nicht ändern | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"ablage":"QA-API-1789899923 Gastnotiz","message":"Ablage gespeichert"}  |
| api-35 | Gast darf Teamdateien nicht lesen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"files":[{"filename":"Full_Stack_Web_Development_FS2025.pdf","uploaded_at":"2025-07-02T08:54:51.522076","uploader":"bob"},{"filename":"helloworld-FS2025-fs.zip","uploaded_at":"202 |
| api-36 | Gast darf Team nicht löschen | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (401, 403); Antwort: {"message":"Team gel\u00f6scht"}  |
| api-37 | Teamname darf nicht nur Leerzeichen enthalten | FEHLER / EINSCHRÄNKUNG | HTTP 201, erwartet (400, 422); Antwort: {"message":"Team created","team_id":4}  |
| api-38 | Umkreissuche benötigt Login | OK | {"http": 401} |
| api-39 | Logout entfernt Zugriff auf Projektliste | FEHLER / EINSCHRÄNKUNG | HTTP 200, erwartet (302, 401, 403); Antwort: &lt;!DOCTYPE html&gt; &lt;html lang="de"&gt;  &lt;head&gt;     &lt;meta charset="UTF-8"&gt;     &lt;title&gt;Projekte des Teams None&lt;/title&gt;     &lt;link rel="stylesheet" href="/static/style.css"&gt;     &lt;style&gt;      |
| extra-01 | Logout: tatsächliche Projektänderung muss gesperrt sein | FEHLER / EINSCHRÄNKUNG | Projektdeadline nach Logout geändert; HTTP 302, gespeichert 2026-12-24T00:00:00 |
| extra-02 | Dateiablage: gleicher Dateiname bleibt eindeutig | FEHLER / EINSCHRÄNKUNG | 2 Dateieinträge für denselben Namen; beide laden 'Version 2' |
| extra-03 | Team mit Mitgliedern und Projekt löschen: keine verwaisten Daten | FEHLER / EINSCHRÄNKUNG | HTTP 200; 1 Projekt(e) ohne zugehöriges Team nach Löschen |
| extra-04 | Bob und Alice senden gleichzeitig: alle 20 Nachrichten bleiben erhalten | FEHLER / EINSCHRÄNKUNG | 20 gesendet, 17 gespeichert; fehlend ['QA-EXTRA-1789900134-parallel-3-1', 'QA-EXTRA-1789900134-parallel-4-2', 'QA-EXTRA-1789900134-parallel-6-2']; HTTP-Status [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200] |
