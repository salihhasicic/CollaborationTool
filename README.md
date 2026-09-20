## Aktueller Stand nach Funktionstest und Fehlerbehebung

Die Fehlerbehebungen und erfolgreichen Nachprüfungen sind in [qa/fixes/BEHEBUNGEN.md](qa/fixes/BEHEBUNGEN.md) dokumentiert. Für die lokale Anwendung beide Python-Server starten:

```sh
.venv/bin/python backend/app.py
# In einem zweiten Terminal:
.venv/bin/python main.py
```

Anmeldung unter http://localhost:3000/login, zum Beispiel `bob` / `5678` oder `alice` / `1234`. Nach diesem Update einmal neu anmelden. Datenbankschema und historische private Nachrichten werden beim Start automatisch und ohne Zurücksetzen der vorhandenen Daten migriert. Für eine vollständig neue Datenbank legt `.venv/bin/python backend/db_init.py` die Demo-Nutzer an.

Dateien gleichen Namens werden als getrennte Versionen gespeichert. Teams mit Mitgliedern oder gespeicherten Daten können nicht gelöscht werden. Private und Teamchats laden neue Nachrichten automatisch nach.

Für echte KI-Antworten wird weiterhin `OPENAI_API_KEY` in der lokalen `.env` benötigt; ohne Schlüssel zeigt die App eine verständliche Meldung. Ein Modell kann bei Bedarf über `OPENAI_MODEL` konfiguriert werden.

# SYNQ – Webbasierte Team-Collaboration-App

SYNQ ist ein Full-Stack Webprojekt (Gruppe 6 im Kurs Full Stack Web Development FS2025) und dient als Collaboration-Tool für Teams. Die Anwendung wurde in Python mit Flask entwickelt und bietet Funktionen zur Bildung von Teams, zur Kommunikation und zum gemeinsamen Arbeiten. Nutzer können Profile mit Foto anlegen, sich zu Teams zusammenschließen und über Chats, Dateiablagen sowie weitere Werkzeuge effektiv zusammenarbeiten. Das Tool enthält neben den Grundfunktionalitäten (Profile, Team-Chat, Suche & Matching) auch Geo-Location-basierte Features, KI-gestützte Antwortvorschläge und ein einfaches Projektmanagement-System.

### Funktionsübersicht

- Benutzerprofile mit Foto: Nutzer können sich registrieren und ein Profil mit Benutzername, Foto, Standort (Ort + Koordinaten) und Skills anlegen. Das Profil zeigt das Foto sowie zusätzliche Angaben wie Standort (mit Karte) und Fähigkeiten an. Das Profilbild kann hochgeladen und geändert werden; Bilder werden im System gespeichert und im Profil angezeigt.

- Team-Bildung und Skill-basiertes Matching: Nutzer können Teams erstellen und verwalten. Ein Nutzer kann genau einem Team angehören. Bei der Registrierung kann optional eine Team-ID angegeben werden, um direkt einem bestehenden Team beizutreten. Alternativ lässt sich ein neues Team gründen. Die Plattform erleichtert das Auffinden passender Teammitglieder durch eine parametrische Suche nach Skills – es können also Nutzer nach bestimmten Fähigkeiten gefiltert werden. (Ein darüber hinausgehender Match-Algorithmus ließe sich auf Basis der Skills realisieren – derzeit erfolgt das Matching über die manuelle Suche.)

- Team-Chat (Gruppenchat): Innerhalb eines Teams können Mitglieder in einem gemeinsamen Chat kommunizieren (1:n Nachrichten). Alle Teammitglieder sehen die gesendeten Nachrichten in Echtzeit (aktuell mittels periodischer Abrufe oder Seitenaktualisierung, da keine WebSocket-Integration erfolgt ist). Neue Nachrichten enthalten Absender, Inhalt und Zeitstempel.

- Private Chats (1:1): Zusätzlich zum Teamchat gibt es die Möglichkeit zu direkten Privatnachrichten zwischen zwei Nutzern. Der Nutzer kann über ein Profil einen privaten Chat starten (Button „💬 Privater Chat“ im Benutzerprofil). Das System speichert diese 1:1-Nachrichten und ermöglicht es, den Gesprächsverlauf zwischen zwei Nutzern jederzeit einzusehen. (Private Nachrichten werden transaktional in SQLite gespeichert; vorhandene JSON-Verläufe werden einmalig migriert.)

- Dateiablage im Team: Für jedes Team steht eine gemeinsame Dateiablage zur Verfügung. Teammitglieder können Dateien hochladen und im Team teilen. Die Dateien werden serverseitig im Ordner backend/uploads gespeichert (pro Team getrennt organisiert). Über die Weboberfläche können Teammitglieder die hochgeladenen Dateien einsehen und herunterladen.

- Geo-Location-Funktionen: Die Anwendung nutzt Standortdaten, um die Zusammenarbeit zu verbessern. Jeder Nutzer kann seinen aktuellen Standort (Breiten- und Längengrad) in seinem Profil speichern. Im Profil wird der Standort auf einer Karte angezeigt (Integration mit Leaflet und OpenStreetMap). Außerdem gibt es eine Funktion, um Nutzer im Umkreis zu finden: Auf der Benutzer-Übersichtsseite kann per Klick auf „Umkreis“ eine Liste nahegelegener Nutzer (im Umkreis von 30 km) angezeigt werden. Diese Berechnung erfolgt über die Haversine-Distanz anhand der gespeicherten Koordinaten.

- KI-Antwortvorschläge: Im Chat-System ist eine Anbindung an die OpenAI-API integriert. Für eingehende Nachrichten können auf Knopfdruck KI-basierte Antwortvorschläge generiert werden. Diese Funktion nutzt GPT-3.5 (via OpenAI API), um einen formulierten Antwortentwurf auf eine gegebene Chat-Nachricht zu liefern. (Die KI-Funktion ist vorbereitet und erfordert einen gültigen API-Schlüssel – siehe Installation – um genutzt zu werden. Sie liefert einen Antworttextvorschlag, den der Nutzer übernehmen oder bearbeiten kann.)

- Projektplanung und Aufgabenverwaltung: SYNQ bietet ein einfaches Projektmanagement-Modul für Teams. Teammitglieder können Projekte erstellen (z. B. gemeinsame Vorhaben oder Arbeitsstreams ihres Teams). Innerhalb jedes Projekts lassen sich Aufgaben/Tasks anlegen, jedem Projektmitglied zuweisen und mit Status verwalten. Vordefinierte Status sind “To Do”, “In Progress” und “Done” zur Nachverfolgung des Arbeitsfortschritts. Eine Projektübersicht zeigt alle Projekte des eigenen Teams, und es gibt Detailansichten für einzelne Projekte mit ihren Tasks sowie Formulare zum Erstellen neuer Projekte und Aufgaben.

### Technologien und Frameworks

Das Projekt wurde mit einem Python/Flask-Stack umgesetzt. Zum Einsatz kommen insbesondere folgende Technologien und Bibliotheken:

- Flask – Micro-Webframework in Python für das Backend und Server-seitige Rendering der Frontend-Seiten. Flask wird hier mit Blueprints strukturiert (Modularisierung der Routen nach Bereichen) und nutzt Jinja2 für die HTML-Templates.

- Datenbank (SQLite) – Verwendung von SQLite als eingebettete Datenbank via Flask-SQLAlchemy (ORM). Das Datenbankschema umfasst Modelle für Benutzer, Teams, Chat-Nachrichten (Teamchat), Projekte und Tasks. Die ORM-Models definieren Beziehungen zwischen diesen Entitäten (z.B. One-to-Many von Team zu User, von Projekt zu Task, etc.). Auch private Nachrichten werden in der Datenbank gespeichert.

- Authentifizierung & Autorisierung – Registrierung und Login werden über Flask-Routen realisiert. Passwörter werden mit Werkzeug gehasht gespeichert. Nach dem Login erhält der Nutzer einen JSON Web Token (JWT) für geschützte API-Aufrufe. Die Bibliothek flask_jwt_extended wird eingesetzt, um JWTs zu erstellen und zu prüfen. Der Token wird als HttpOnly-Cookie gespeichert; Browseranfragen laufen über einen geschützten Proxy auf derselben Origin. Beim Logout wird der Token serverseitig widerrufen.

- Frontend-Technologien – Die Oberfläche besteht aus HTML5-/CSS3-Templates (gerendert durch Flask) und etwas JavaScript für interaktive Funktionen. Es gibt ein globales Stylesheet (static/style.css) mit vordefinierten CSS-Variablen und Klassen für ein konsistentes Design (Farben, Abstände, Buttons etc.). Die UI ist responsiv und im modernen Flat-Design gestaltet (z.B. runde Profilbilder mit Rahmen, Badges für Skills). Icons für Navigation (Dashboard, Projekte, Chat, Team, Profil, Logout) liegen als SVG-Dateien vor und werden im Menü verwendet.

- Leaflet (OpenStreetMap) – Für die Kartenanzeige auf dem Profil wird Leaflet JS genutzt. Über das CDN eingebunden, ermöglicht Leaflet die Darstellung einer interaktiven Karte mit Marker für den Nutzerstandort. Der Nutzer kann seinen aktuellen Standort über die Browser-Geolocation ermitteln lassen; die Koordinaten werden dann im Profil angezeigt und gespeichert.

- OpenAI API – Zur Realisierung der KI-Antwortvorschläge im Chat ist die OpenAI Python-Bibliothek eingebunden. Über die ChatCompletion-Schnittstelle (Model gpt-3.5-turbo) wird basierend auf der letzten empfangenen Nachricht ein Antwortvorschlag generiert. Diese Funktion wird serverseitig in einer Utility-Funktion aufgerufen und liefert einen vom Modell erdachten Antworttext zurück. (Hinweis: Ein gültiger API-Key muss konfiguriert sein, siehe weiter unten.)

- Weitere Libraries: Flask-CORS wird eingesetzt, um Cross-Origin-Aufrufe zwischen Frontend (Port 3000) und Backend-API (Port 5001) zu erlauben (wichtig für das getrennte Running der Komponenten während der Entwicklung). Requests (Python) wird im Frontend-Server genutzt, um die interne API aufzurufen. Zudem kommen einige Standardbibliotheken zum Einsatz (datetime, math für Distanzberechnung, os, uuid für Dateioperationen, etc.).

### Installationsanleitung (lokal ausführen)

Folgende Schritte erläutern, wie man das Projekt lokal installiert und startet:

1. Code beziehen: Entpacken Sie das Projektarchiv Gruppe6_FullStack (z.B. helloworld-FS2025-fs-main.zip) in ein Verzeichnis Ihrer Wahl. Wechseln Sie anschließend in dieses Projektverzeichnis (es sollte u.a. die Dateien main.py, den Ordner backend/, static/ und templates/ enthalten).

2. Python-Umgebung einrichten: Stellen Sie sicher, dass Python 3 (empfohlen Version 3.9 oder höher) installiert ist. Erstellen Sie optional ein virtuelles Environment, um Abhängigkeiten isoliert zu installieren:
```
python3 -m venv venv

source venv/bin/activate   # bei Linux/macOS

venv\Scripts\activate      # bei Windows
```
3. Abhängigkeiten installieren: Installieren Sie die benötigten Python-Pakete mittels pip. Eine vollständige Liste befindet sich in der Datei requirements.txt. Führen Sie im Projektordner aus:
```
pip install -r backend/requirements.txt
```
Hinweis: Sollten Pakete fehlen, prüfen Sie bitte die unten angefügte Liste Requirements (ergänzt) und installieren Sie diese ggf. manuell mit pip install <Paketname>.

4. OpenAI API-Key konfigurieren: Für die Nutzung der KI-Funktion brauchen Sie einen gültigen API-Schlüssel von OpenAI. Legen Sie im Projektverzeichnis eine Datei .env an und fügen Sie Ihre Key ein:
```
OPENAI_API_KEY="sk-...."  
```
Wenn kein Key vorhanden ist, können Sie die KI-Features vorerst nicht verwenden – alle anderen Funktionen der App stehen dennoch zur Verfügung (ggf. erscheint eine Fehlermeldung, wenn versucht wird, einen Antwortvorschlag abzurufen).

5. Datenbank initialisieren: Das Projekt verwendet SQLite als lokale Datenbank. Um das Schema anzulegen und Beispieldaten einzuspielen, führen Sie einmalig das Skript backend/db_init.py aus:
```
python backend/db_init.py
```
Dadurch wird die SQLite-DB-Datei backend/instance/collab.db angelegt. Vorhandene Nutzer und Teams bleiben bei erneutem Aufruf erhalten. Es werden auch Demo-Daten angelegt, u.a. drei Beispiel-Teams (Dev Team, Design Team, AI Team) und mehrere Beispielnutzer (Alice, Bob, Carla, …) mit voreingestellten Profilen und Teams. Die Demo-User haben einfache Passwörter (z.B. Benutzer alice mit Passwort 1234), die zum Testen verwendet werden können. Ein weiterer Demo-Zugang ist bob mit Passwort 5678.

6. Backend-Server starten: Starten Sie nun die Flask-App für das Backend (API) durch Ausführen von backend/app.py:
```
python backend/app.py
```
Der API-Server läuft per Voreinstellung auf http://127.0.0.1:5001, um den macOS-Port 5000 zu vermeiden. Für einen anderen Port setzen Sie BACKEND_PORT beim Backend und die passende BACKEND_URL beim Frontend. Sie sollten im Terminal sehen, dass Flask im Debug-Modus startet. Lassen Sie dieses Terminal offen, da hier Logs für API-Aufrufe erscheinen (und der Server ansonsten beendet würde).

7. Frontend-Server starten: Öffnen Sie ein zweites Terminal-Fenster bzw. eine neue Shell. Starten Sie die Flask-App für das Frontend durch:
```
python main.py
```
Diese Serverinstanz läuft standardmäßig auf http://127.0.0.1:3000 (Port 3000). Auch hier sollten Sie im Terminal Flask-Startmeldungen sehen.

8. Anwendung im Browser öffnen: Rufen Sie in Ihrem Webbrowser die URL http://localhost:3000/ auf. Sie sollten die Startseite („Willkommen zur Teams Messaging App“) sehen. Von hier aus können Sie sich registrieren oder mit einem bestehenden Account anmelden. Nutzen Sie z.B. einen der Demo-Accounts (siehe Schritt 5) oder legen Sie über Registrieren einen neuen Benutzer an.

SYNQ – Webbasierte Team-Collaboration-App

SYNQ ist ein Full-Stack Webprojekt (Gruppe 6 im Kurs Full Stack Web Development FS2025) und dient als Collaboration-Tool für Teams. Die Anwendung wurde in Python mit Flask entwickelt und bietet Funktionen zur Bildung von Teams, zur Kommunikation und zum gemeinsamen Arbeiten. Nutzer können Profile mit Foto anlegen, sich zu Teams zusammenschließen und über Chats, Dateiablagen sowie weitere Werkzeuge effektiv zusammenarbeiten. Das Tool enthält neben den Grundfunktionalitäten (Profile, Team-Chat, Suche & Matching) auch Geo-Location-basierte Features, KI-gestützte Antwortvorschläge und ein einfaches Projektmanagement-System.

Funktionsübersicht

Benutzerprofile mit Foto: Nutzer können sich registrieren und ein Profil mit Benutzername, Foto, Standort (Ort + Koordinaten) und Skills anlegen. Das Profil zeigt das Foto sowie zusätzliche Angaben wie Standort (mit Karte) und Fähigkeiten an. Das Profilbild kann hochgeladen und geändert werden; Bilder werden im System gespeichert und im Profil angezeigt.

Team-Bildung und Skill-basiertes Matching: Nutzer können Teams erstellen und verwalten. Ein Nutzer kann genau einem Team angehören. Bei der Registrierung kann optional eine Team-ID angegeben werden, um direkt einem bestehenden Team beizutreten. Alternativ lässt sich ein neues Team gründen. Die Plattform erleichtert das Auffinden passender Teammitglieder durch eine parametrische Suche nach Skills – es können also Nutzer nach bestimmten Fähigkeiten gefiltert werden. (Ein darüber hinausgehender Match-Algorithmus ließe sich auf Basis der Skills realisieren – derzeit erfolgt das Matching über die manuelle Suche.)

Team-Chat (Gruppenchat): Innerhalb eines Teams können Mitglieder in einem gemeinsamen Chat kommunizieren (1:n Nachrichten). Alle Teammitglieder sehen die gesendeten Nachrichten in Echtzeit (aktuell mittels periodischer Abrufe oder Seitenaktualisierung, da keine WebSocket-Integration erfolgt ist). Neue Nachrichten enthalten Absender, Inhalt und Zeitstempel.

Private Chats (1:1): Zusätzlich zum Teamchat gibt es die Möglichkeit zu direkten Privatnachrichten zwischen zwei Nutzern. Der Nutzer kann über ein Profil einen privaten Chat starten (Button „💬 Privater Chat“ im Benutzerprofil). Das System speichert diese 1:1-Nachrichten und ermöglicht es, den Gesprächsverlauf zwischen zwei Nutzern jederzeit einzusehen. (Private Nachrichten werden transaktional in SQLite gespeichert; vorhandene JSON-Verläufe werden einmalig migriert.)

Dateiablage im Team: Für jedes Team steht eine gemeinsame Dateiablage zur Verfügung. Teammitglieder können Dateien hochladen und im Team teilen. Die Dateien werden serverseitig im Ordner backend/uploads gespeichert (pro Team getrennt organisiert). Über die Weboberfläche können Teammitglieder die hochgeladenen Dateien einsehen und herunterladen.

Geo-Location-Funktionen: Die Anwendung nutzt Standortdaten, um die Zusammenarbeit zu verbessern. Jeder Nutzer kann seinen aktuellen Standort (Breiten- und Längengrad) in seinem Profil speichern. Im Profil wird der Standort auf einer Karte angezeigt (Integration mit Leaflet und OpenStreetMap). Außerdem gibt es eine Funktion, um Nutzer im Umkreis zu finden: Auf der Benutzer-Übersichtsseite kann per Klick auf „Umkreis“ eine Liste nahegelegener Nutzer (im Umkreis von 30 km) angezeigt werden. Diese Berechnung erfolgt über die Haversine-Distanz anhand der gespeicherten Koordinaten.

KI-Antwortvorschläge: Im Chat-System ist eine Anbindung an die OpenAI-API integriert. Für eingehende Nachrichten können auf Knopfdruck KI-basierte Antwortvorschläge generiert werden. Diese Funktion nutzt GPT-3.5 (via OpenAI API), um einen formulierten Antwortentwurf auf eine gegebene Chat-Nachricht zu liefern. (Die KI-Funktion ist vorbereitet und erfordert einen gültigen API-Schlüssel – siehe Installation – um genutzt zu werden. Sie liefert einen Antworttextvorschlag, den der Nutzer übernehmen oder bearbeiten kann.)

Projektplanung und Aufgabenverwaltung: SYNQ bietet ein einfaches Projektmanagement-Modul für Teams. Teammitglieder können Projekte erstellen (z. B. gemeinsame Vorhaben oder Arbeitsstreams ihres Teams). Innerhalb jedes Projekts lassen sich Aufgaben/Tasks anlegen, jedem Projektmitglied zuweisen und mit Status verwalten. Vordefinierte Status sind “To Do”, “In Progress” und “Done” zur Nachverfolgung des Arbeitsfortschritts. Eine Projektübersicht zeigt alle Projekte des eigenen Teams, und es gibt Detailansichten für einzelne Projekte mit ihren Tasks sowie Formulare zum Erstellen neuer Projekte und Aufgaben.

Technologien und Frameworks

Das Projekt wurde mit einem Python/Flask-Stack umgesetzt. Zum Einsatz kommen insbesondere folgende Technologien und Bibliotheken:

Flask – Micro-Webframework in Python für das Backend und Server-seitige Rendering der Frontend-Seiten. Flask wird hier mit Blueprints strukturiert (Modularisierung der Routen nach Bereichen) und nutzt Jinja2 für die HTML-Templates.

Datenbank (SQLite) – Verwendung von SQLite als eingebettete Datenbank via Flask-SQLAlchemy (ORM). Das Datenbankschema umfasst Modelle für Benutzer, Teams, Chat-Nachrichten (Teamchat), Projekte und Tasks. Die ORM-Models definieren Beziehungen zwischen diesen Entitäten (z.B. One-to-Many von Team zu User, von Projekt zu Task, etc.). Auch private Nachrichten werden in der Datenbank gespeichert.

Authentifizierung & Autorisierung – Registrierung und Login werden über Flask-Routen realisiert. Passwörter werden mit Werkzeug gehasht gespeichert. Nach dem Login erhält der Nutzer einen JSON Web Token (JWT) für geschützte API-Aufrufe. Die Bibliothek flask_jwt_extended wird eingesetzt, um JWTs zu erstellen und zu prüfen. Der Token wird als HttpOnly-Cookie gespeichert; Browseranfragen laufen über einen geschützten Proxy auf derselben Origin. Beim Logout wird der Token serverseitig widerrufen.

Frontend-Technologien – Die Oberfläche besteht aus HTML5-/CSS3-Templates (gerendert durch Flask) und etwas JavaScript für interaktive Funktionen. Es gibt ein globales Stylesheet (static/style.css) mit vordefinierten CSS-Variablen und Klassen für ein konsistentes Design (Farben, Abstände, Buttons etc.). Die UI ist responsiv und im modernen Flat-Design gestaltet (z.B. runde Profilbilder mit Rahmen, Badges für Skills). Icons für Navigation (Dashboard, Projekte, Chat, Team, Profil, Logout) liegen als SVG-Dateien vor und werden im Menü verwendet.

Leaflet (OpenStreetMap) – Für die Kartenanzeige auf dem Profil wird Leaflet JS genutzt. Über das CDN eingebunden, ermöglicht Leaflet die Darstellung einer interaktiven Karte mit Marker für den Nutzerstandort. Der Nutzer kann seinen aktuellen Standort über die Browser-Geolocation ermitteln lassen; die Koordinaten werden dann im Profil angezeigt und gespeichert.

OpenAI API – Zur Realisierung der KI-Antwortvorschläge im Chat ist die OpenAI Python-Bibliothek eingebunden. Über die ChatCompletion-Schnittstelle (Model gpt-3.5-turbo) wird basierend auf der letzten empfangenen Nachricht ein Antwortvorschlag generiert. Diese Funktion wird serverseitig in einer Utility-Funktion aufgerufen und liefert einen vom Modell erdachten Antworttext zurück. (Hinweis: Ein gültiger API-Key muss konfiguriert sein, siehe weiter unten.)

Weitere Libraries: Flask-CORS wird eingesetzt, um Cross-Origin-Aufrufe zwischen Frontend (Port 3000) und Backend-API (Port 5001) zu erlauben (wichtig für das getrennte Running der Komponenten während der Entwicklung). Requests (Python) wird im Frontend-Server genutzt, um die interne API aufzurufen. Zudem kommen einige Standardbibliotheken zum Einsatz (datetime, math für Distanzberechnung, os, uuid für Dateioperationen, etc.).

Installationsanleitung (lokal ausführen)

Folgende Schritte erläutern, wie man das Projekt lokal installiert und startet:

Code beziehen: Entpacken Sie das Projektarchiv Gruppe6_FullStack (z.B. helloworld-FS2025-fs-main.zip) in ein Verzeichnis Ihrer Wahl. Wechseln Sie anschließend in dieses Projektverzeichnis (es sollte u.a. die Dateien main.py, den Ordner backend/, static/ und templates/ enthalten).

Python-Umgebung einrichten: Stellen Sie sicher, dass Python 3 (empfohlen Version 3.9 oder höher) installiert ist. Erstellen Sie optional ein virtuelles Environment, um Abhängigkeiten isoliert zu installieren:

bash

Kopieren

Bearbeiten

python3 -m venv venv

source venv/bin/activate   # bei Linux/macOS

venv\Scripts\activate      # bei Windows

Abhängigkeiten installieren: Installieren Sie die benötigten Python-Pakete mittels pip. Eine vollständige Liste befindet sich in der Datei requirements.txt. Führen Sie im Projektordner aus:

pip install -r backend/requirements.txt

Hinweis: Sollten Pakete fehlen, prüfen Sie bitte die unten angefügte Liste Requirements (ergänzt) und installieren Sie diese ggf. manuell mit pip install <Paketname>.

OpenAI API-Key konfigurieren (optional): Für die Nutzung der KI-Funktion brauchen Sie einen gültigen API-Schlüssel von OpenAI. Legen Sie im Projektverzeichnis eine Datei .env an und fügen Sie Ihre Key ein:

OPENAI_API_KEY="sk-...."  

Wenn kein Key vorhanden ist, können Sie die KI-Features vorerst nicht verwenden – alle anderen Funktionen der App stehen dennoch zur Verfügung (ggf. erscheint eine Fehlermeldung, wenn versucht wird, einen Antwortvorschlag abzurufen).

Datenbank initialisieren: Das Projekt verwendet SQLite als lokale Datenbank. Um das Schema anzulegen und Beispieldaten einzuspielen, führen Sie einmalig das Skript backend/db_init.py aus:

python backend/db_init.py

Dadurch wird die SQLite-DB-Datei backend/instance/collab.db angelegt. Vorhandene Nutzer und Teams bleiben bei erneutem Aufruf erhalten. Es werden auch Demo-Daten angelegt, u.a. drei Beispiel-Teams (Dev Team, Design Team, AI Team) und mehrere Beispielnutzer (Alice, Bob, Carla, …) mit voreingestellten Profilen und Teams. Die Demo-User haben einfache Passwörter (z.B. Benutzer alice mit Passwort 1234), die zum Testen verwendet werden können. Ein weiterer Demo-Zugang ist bob mit Passwort 5678.

Backend-Server starten: Starten Sie nun die Flask-App für das Backend (API) durch Ausführen von backend/app.py:

python backend/app.py

Der API-Server läuft per Voreinstellung auf http://127.0.0.1:5001, um den macOS-Port 5000 zu vermeiden. Für einen anderen Port setzen Sie BACKEND_PORT beim Backend und die passende BACKEND_URL beim Frontend. Sie sollten im Terminal sehen, dass Flask im Debug-Modus startet. Lassen Sie dieses Terminal offen, da hier Logs für API-Aufrufe erscheinen (und der Server ansonsten beendet würde).

Frontend-Server starten: Öffnen Sie ein zweites Terminal-Fenster bzw. eine neue Shell. Starten Sie die Flask-App für das Frontend durch:

python main.py

Diese Serverinstanz läuft standardmäßig auf http://127.0.0.1:3000 (Port 3000). Auch hier sollten Sie im Terminal Flask-Startmeldungen sehen.

Anwendung im Browser öffnen: Rufen Sie in Ihrem Webbrowser die URL http://localhost:3000/ auf. Sie sollten die Startseite („Willkommen zur Teams Messaging App“) sehen. Von hier aus können Sie sich registrieren oder mit einem bestehenden Account anmelden. Nutzen Sie z.B. einen der Demo-Accounts (siehe Schritt 5) oder legen Sie über Registrieren einen neuen Benutzer an.

Nutzungshinweise

Nach erfolgreichem Start der beiden Serverkomponenten kann die Anwendung über den Browser genutzt werden. Hier einige Hinweise zur Verwendung der wichtigsten Funktionen:

Registrierung und Login: Neue Benutzer können sich über Registrieren einen Account anlegen. Erforderlich sind ein Benutzername und Passwort; optional können bereits ein Standort (Wohnort), Skills sowie ein Team angegeben werden. Falls Sie ein Team angeben, nutzen Sie die Team-ID (z.B. 1 für Dev Team, 2 für Design Team, etc., sofern bekannt). Nach der Registrierung können Sie sich mit den Zugangsdaten anmelden. – Alternativ nutzen Sie einen Demo-Account (siehe oben, z.B. Benutzer alice/1234). Nach dem Login wird auf das Dashboard weitergeleitet.

Dashboard & Navigation: Die linke Seitenleiste bietet Navigation zu allen Hauptbereichen:

Dashboard – Übersicht (hier könnten künftig z.B. Neuigkeiten oder ein Team-Overview erscheinen; aktuell zeigt das Dashboard vor allem Willkommensgrüße).

Projekte – Projektübersicht des eigenen Teams (siehe unten).

Benutzer – Liste aller Benutzer der Plattform, mit Such- und Umkreis-Filtern.

Chat – Übersicht der privaten Chats (1:1-Chats) des eingeloggten Nutzers.

Team – Details zum Team des Nutzers (sichtbar, wenn man bereits in einem Team ist).

Team-Chat – Gruppenchat-Seite für das Team (sichtbar, wenn man einem Team angehört).

Team verwalten – Seite zum Verlassen oder Erstellen eines Teams (sichtbar, wenn angemeldet; ermöglicht Team-Gründung, falls man noch keinem Team beigetreten ist).

Mein Profil – Profilseite des eingeloggten Nutzers (zeigt eigene Daten, ermöglicht Änderungen).

Logout – Abmelden des Nutzers.

Profil anzeigen & bearbeiten: Auf der Profilseite werden Ihre hinterlegten Daten angezeigt: Benutzername, Foto, Ort, Koordinaten (Latitude/Longitude) sowie Skills. Wenn Sie Koordinaten gespeichert haben, wird darunter eine Karte mit Ihrem Standortmarker angezeigt. Über einen Button (Kompass-Symbol) können Sie Ihren aktuellen Standort ermitteln lassen: Die Anwendung fragt dann die Browser-Geolocation ab und zeigt die ermittelten Koordinaten an. Mit Speichern (erscheint neben den Feldern) können Sie diese in Ihrem Profil übernehmen. Ebenso lässt sich über Durchsuchen... ein neues Profilfoto hochladen; dieses wird nach dem Upload aktualisiert angezeigt.

Teams erstellen oder beitreten: Wenn Sie noch in keinem Team sind (z.B. nach Neuregistrierung ohne Team), können Sie über Team verwalten ein neues Team gründen. Geben Sie einen Teamnamen ein und bestätigen Sie. Anschließend wird das Team erstellt und Ihr Benutzer wird Mitglied dieses Teams. (Hinweis: Um einem bestehenden Team beizutreten, muss derzeit die Team-ID bereits bei der Registrierung angegeben werden. Eine komfortable Invite- oder Join-Funktion kann in Zukunft ergänzt werden.) Sobald Sie Mitglied eines Teams sind, erscheinen in der Navigation zusätzliche Punkte (Team, Team-Chat) für teambezogene Funktionen.

Team-Übersicht: Über Team in der Navigation gelangen Sie zur Team-Detailseite. Dort sehen Sie den Teamnamen und eine Liste der Mitglieder Ihres Teams. Jedes Mitglied wird mit Benutzernamen (und ggf. Profilbild) angezeigt. Teammitglieder können von hier aus via Klick auf ihren Namen oder das Chat-Symbol direkt per privater Nachricht kontaktiert werden. Der Team-Owner kann an dieser Stelle in zukünftigen Versionen Mitglieder verwalten (derzeit ist diese Funktion begrenzt).

Team-Chat (Gruppenchat): Unter Team-Chat öffnet sich der gemeinsame Chatraum Ihres aktuellen Teams. In diesem Chat können alle Teammitglieder Nachrichten an die Gruppe senden. Geben Sie eine Nachricht in das Textfeld ein und klicken Sie auf Senden. Die Nachricht wird dann mit Ihrem Namen, Zeitstempel etc. im Chatverlauf angezeigt. Alle Teammitglieder, die gerade online sind, sehen neue Nachrichten (aktuell muss ggf. der Chat manuell neu geladen werden, da keine Live-Pushes implementiert sind). Ungelesene Nachrichten werden beim Öffnen der Chatseite geladen. – KI-Antworthilfe: Zu jeder Nachricht im Teamchat kann ein KI-gestützter Antwortvorschlag angefordert werden. Klicken Sie dafür auf den Button „🤖 Vorschlag“ neben einer empfangenen Nachricht (sofern vorhanden). Das System ruft daraufhin die OpenAI-API auf und zeigt nach kurzer Zeit einen Formulierungsvorschlag an, den Sie bei Bedarf bearbeiten und absenden können. (Die KI-Funktion steht nur zur Verfügung, wenn ein API-Key konfiguriert wurde. Andernfalls erhalten Sie einen Hinweis.)

Private 1:1-Chat: Über die Benutzerliste oder ein Profil können Sie einen privaten Chat mit einem anderen Nutzer starten. Klicken Sie z.B. in der Benutzer-Übersicht bei der gewünschten Person auf „Privater Chat“. Es öffnet sich eine Chat-Seite ähnlich dem Teamchat, jedoch nur zwischen Ihnen und dem gewählten Nutzer. Sie können hier Nachrichten austauschen, die nur von Ihnen beiden einsehbar sind. Ihre laufenden privaten Unterhaltungen werden unter Chat (Navigationspunkt) als Liste angezeigt, sodass Sie jederzeit einen begonnenen Dialog wieder aufnehmen können. (Intern speichert die Anwendung diese Unterhaltungen in einer JSON-Datei; in zukünftigen Versionen könnte dies in die Datenbank überführt werden.)

Benutzersuche nach Skills: Die Seite Benutzerübersicht listet standardmäßig alle registrierten Nutzer auf, mit ihren Profilbildern, Namen, Skills und Aktionen (Profil ansehen, private Nachricht senden). Über das Eingabefeld „Suche nach Skill“ können Sie die Liste filtern. Geben Sie einen Skill oder Teil davon ein (z.B. "Python") und klicken Sie auf Suchen. Es werden dann nur Nutzer angezeigt, die diesen Begriff in ihren hinterlegten Skills haben. So finden Sie schnell Personen mit bestimmten Fähigkeiten (z.B. Programmierkenntnissen).

Nutzer in der Nähe finden: Ebenfalls auf der Benutzer-Seite können Sie per Klick auf „Umkreis“ andere Nutzer in Ihrer geografischen Nähe ermitteln. Voraussetzung: Sie selbst haben Ihren Standort (Lat, Lng) im Profil gesetzt. Die Anwendung ruft dann die API /user/nearby auf, welche mithilfe der Haversine-Formel alle Nutzer innerhalb eines Radius von 30 km findet. Das Ergebnis wird direkt auf der Seite unterhalb des Suchformulars als Liste angezeigt – inklusive Entfernungsangabe in Kilometern zu jedem gefundenen Nutzer. So können Sie z.B. Teammitglieder in Ihrer Umgebung identifizieren. (Hinweis: Diese Funktion erfordert einen aktiven Login und den zuvor erwähnten JWT-Token im Browser, da der API-Endpunkt geschützt ist.)

Projekte und Aufgaben: Über den Menüpunkt Projekte gelangen Sie zur Projektverwaltung Ihres Teams. Hier sind alle Projekte aufgelistet, die von Teammitgliedern angelegt wurden. Zu jedem Projekt wird der Name und der Status angezeigt (bspw. In Progress oder Done). Sie können ein neues Projekt erstellen, indem Sie auf „Projekt anlegen“ klicken und einen Namen eingeben. In der Projekt-Detailansicht sehen Sie die Liste der dazugehörigen Tasks/Aufgaben. Für jedes Projekt können neue Aufgaben hinzugefügt werden („Task anlegen“), wobei Sie einen Titel, eine Beschreibung, einen Verantwortlichen (Teammitglied) und optional eine Deadline angeben können. Aufgaben erscheinen mit ihrem Titel, Status und ggf. zuständigem Benutzer in der Liste. Der Status einer Aufgabe kann per Klick geändert werden (z.B. von To Do auf Done, wenn erledigt) – hierzu gibt es Buttons oder Dropdowns neben der Aufgabe. Dieses einfache Projektmanagement-Feature ermöglicht es dem Team, gemeinsame Todos zu verfolgen und zu bearbeiten.

Dateiablage nutzen: Innerhalb eines Teams können Dateien zentral gespeichert werden. Über die Team-Seite oder direkt beim Chat finden Sie einen Bereich Dateiablage. Mit Durchsuchen/Datei auswählen können Sie eine Datei von Ihrem Rechner auswählen und hochladen. Alle hochgeladenen Dateien werden in einer Liste angezeigt – inkl. Dateiname, Upload-Datum und Uploader. Teammitglieder können die Dateien über einen Klick auf den Dateinamen herunterladen. Dieses Feature erleichtert den Austausch von Dokumenten, Bildern etc. im Team. Die Ablage ist teamweit sichtbar; es empfiehlt sich daher, nur für das Team relevante Dateien hochzuladen.

Hinweise zur Weiterentwicklung

Diese Anwendung ist ein Prototyp, der im Rahmen eines Lernszenarios entstanden ist. Einige mögliche Erweiterungs- oder Verbesserungsansätze für zukünftige Versionen sind:

Echte Echtzeit-Kommunikation: Derzeit werden Chatnachrichten durch regelmäßiges Abfragen dargestellt. Durch Integration von WebSockets (z.B. via Flask-SocketIO) ließe sich ein in Echtzeit aktualisierter Chat umsetzen, inklusive Live-Statusanzeigen (Benutzer online/offline, „schreibt gerade…“ etc.). Ebenso könnten Benachrichtigungen bei neuen Nachrichten oder Team-Ereignissen in Echtzeit erscheinen.

Verbesserte Team-Verwaltung: Momentan kann ein Nutzer nur einem Team angehören. Künftige Versionen könnten Einladungslinks oder Team-Codes bereitstellen, um den Beitritt zu Teams nach der Registrierung zu erleichtern. Auch Rollen innerhalb des Teams (Admin/Member) und Berechtigungen (z.B. nur Team-Admin darf Mitglieder hinzufügen oder entfernen) wären denkbar.

Private Chats in Datenbank speichern: Die 1:1-Chats werden aktuell in einer JSON-Datei persistiert, was für den Prototyp ausreichend ist. Eine Weiterentwicklung sollte diese jedoch in ein eigenes Datenbankmodell (mit Beziehungen zu Usern) überführen, um Skalierbarkeit und Abfragefunktionen (z.B. anzeige der letzten Nachricht, ungelesene Nachrichten) zu verbessern.

Projektmanagement ausbauen: Das vorhandene Projekt- und Task-Feature ließe sich erweitern, z.B. mit Kommentarfunktionen pro Task, Dateien pro Task anhängen, Prioritäten, oder Kanban-ähnliche Boards. Eine Kalenderansicht für Deadlines oder eine Benachrichtigung bei nahendem Fälligkeitsdatum wären praktische Ergänzungen.

KI-Integration vertiefen: Die KI-Antworthilfe kann ausgebaut werden, etwa indem automatisch Antwortvorschläge erscheinen oder verschiedene Tonalitäten gewählt werden können. Zudem könnten KI-Features wie automatische Zusammenfassungen langer Chatverläufe oder das Vorschlagen von passenden Teammitgliedern basierend auf Skills hinzukommen.

Security & Deployment: Für den produktiven Einsatz sollten Sicherheitsmaßnahmen vertieft werden (z.B. Eingabefilter, Rate Limiting für APIs, Bild-Upload-Validierung). Auch die Konfiguration für unterschiedliche Umgebungen (Development vs. Production) und die Bereitstellung via WSGI-Server (z.B. Gunicorn) in der Cloud wären nächsinnvoll, inkl. eines Containerizations (Docker) für einfachere Deployments.python main.py

Diese Serverinstanz läuft standardmäßig auf http://127.0.0.1:3000 (Port 3000). Auch hier sollten Sie im Terminal Flask-Startmeldungen sehen.

Anwendung im Browser öffnen: Rufen Sie in Ihrem Webbrowser die URL http://localhost:3000/ auf. Sie sollten die Startseite („Willkommen zur Teams Messaging App“) sehen. Von hier aus können Sie sich registrieren oder mit einem bestehenden Account anmelden. Nutzen Sie z.B. einen der Demo-Accounts (siehe Schritt 5) oder legen Sie über Registrieren einen neuen Benutzer an.

### Nutzungshinweise

Nach erfolgreichem Start der beiden Serverkomponenten kann die Anwendung über den Browser genutzt werden. Hier einige Hinweise zur Verwendung der wichtigsten Funktionen:

Registrierung und Login: Neue Benutzer können sich über Registrieren einen Account anlegen. Erforderlich sind ein Benutzername und Passwort; optional können bereits ein Standort (Wohnort), Skills sowie ein Team angegeben werden. Falls Sie ein Team angeben, nutzen Sie die Team-ID (z.B. 1 für Dev Team, 2 für Design Team, etc., sofern bekannt). Nach der Registrierung können Sie sich mit den Zugangsdaten anmelden. – Alternativ nutzen Sie einen Demo-Account (siehe oben, z.B. Benutzer alice/1234). Nach dem Login wird auf das Dashboard weitergeleitet.

Dashboard & Navigation: Die linke Seitenleiste bietet Navigation zu allen Hauptbereichen:

- Dashboard – Übersicht (hier könnten künftig z.B. Neuigkeiten oder ein Team-Overview erscheinen; aktuell zeigt das Dashboard vor allem Willkommensgrüße).

- Projekte – Projektübersicht des eigenen Teams (siehe unten).

- Benutzer – Liste aller Benutzer der Plattform, mit Such- und Umkreis-Filtern.

- Chat – Übersicht der privaten Chats (1:1-Chats) des eingeloggten Nutzers.

- Team – Details zum Team des Nutzers (sichtbar, wenn man bereits in einem Team ist).

- Team-Chat – Gruppenchat-Seite für das Team (sichtbar, wenn man einem Team angehört).

- Team verwalten – Seite zum Verlassen oder Erstellen eines Teams (sichtbar, wenn angemeldet; ermöglicht Team-Gründung, falls man noch keinem Team beigetreten ist).

- Mein Profil – Profilseite des eingeloggten Nutzers (zeigt eigene Daten, ermöglicht Änderungen).

- Logout – Abmelden des Nutzers.

Profil anzeigen & bearbeiten: Auf der Profilseite werden Ihre hinterlegten Daten angezeigt: Benutzername, Foto, Ort, Koordinaten (Latitude/Longitude) sowie Skills. Wenn Sie Koordinaten gespeichert haben, wird darunter eine Karte mit Ihrem Standortmarker angezeigt. Über einen Button (Kompass-Symbol) können Sie Ihren aktuellen Standort ermitteln lassen: Die Anwendung fragt dann die Browser-Geolocation ab und zeigt die ermittelten Koordinaten an. Mit Speichern (erscheint neben den Feldern) können Sie diese in Ihrem Profil übernehmen. Ebenso lässt sich über Durchsuchen... ein neues Profilfoto hochladen; dieses wird nach dem Upload aktualisiert angezeigt.

Teams erstellen oder beitreten: Wenn Sie noch in keinem Team sind (z.B. nach Neuregistrierung ohne Team), können Sie über Team verwalten ein neues Team gründen. Geben Sie einen Teamnamen ein und bestätigen Sie. Anschließend wird das Team erstellt und Ihr Benutzer wird Mitglied dieses Teams. (Hinweis: Um einem bestehenden Team beizutreten, muss derzeit die Team-ID bereits bei der Registrierung angegeben werden. Eine komfortable Invite- oder Join-Funktion kann in Zukunft ergänzt werden.) Sobald Sie Mitglied eines Teams sind, erscheinen in der Navigation zusätzliche Punkte (Team, Team-Chat) für teambezogene Funktionen.

Team-Übersicht: Über Team in der Navigation gelangen Sie zur Team-Detailseite. Dort sehen Sie den Teamnamen und eine Liste der Mitglieder Ihres Teams. Jedes Mitglied wird mit Benutzernamen (und ggf. Profilbild) angezeigt. Teammitglieder können von hier aus via Klick auf ihren Namen oder das Chat-Symbol direkt per privater Nachricht kontaktiert werden. Der Team-Owner kann an dieser Stelle in zukünftigen Versionen Mitglieder verwalten (derzeit ist diese Funktion begrenzt).

Team-Chat (Gruppenchat): Unter Team-Chat öffnet sich der gemeinsame Chatraum Ihres aktuellen Teams. In diesem Chat können alle Teammitglieder Nachrichten an die Gruppe senden. Geben Sie eine Nachricht in das Textfeld ein und klicken Sie auf Senden. Die Nachricht wird dann mit Ihrem Namen, Zeitstempel etc. im Chatverlauf angezeigt. Alle Teammitglieder, die gerade online sind, sehen neue Nachrichten (aktuell muss ggf. der Chat manuell neu geladen werden, da keine Live-Pushes implementiert sind). Ungelesene Nachrichten werden beim Öffnen der Chatseite geladen. – KI-Antworthilfe: Zu jeder Nachricht im Teamchat kann ein KI-gestützter Antwortvorschlag angefordert werden. Klicken Sie dafür auf den Button „🤖 Vorschlag“ neben einer empfangenen Nachricht (sofern vorhanden). Das System ruft daraufhin die OpenAI-API auf und zeigt nach kurzer Zeit einen Formulierungsvorschlag an, den Sie bei Bedarf bearbeiten und absenden können. (Die KI-Funktion steht nur zur Verfügung, wenn ein API-Key konfiguriert wurde. Andernfalls erhalten Sie einen Hinweis.)

Private 1:1-Chat: Über die Benutzerliste oder ein Profil können Sie einen privaten Chat mit einem anderen Nutzer starten. Klicken Sie z.B. in der Benutzer-Übersicht bei der gewünschten Person auf „Privater Chat“. Es öffnet sich eine Chat-Seite ähnlich dem Teamchat, jedoch nur zwischen Ihnen und dem gewählten Nutzer. Sie können hier Nachrichten austauschen, die nur von Ihnen beiden einsehbar sind. Ihre laufenden privaten Unterhaltungen werden unter Chat (Navigationspunkt) als Liste angezeigt, sodass Sie jederzeit einen begonnenen Dialog wieder aufnehmen können. (Intern speichert die Anwendung diese Unterhaltungen in einer JSON-Datei; in zukünftigen Versionen könnte dies in die Datenbank überführt werden.)

Benutzersuche nach Skills: Die Seite Benutzerübersicht listet standardmäßig alle registrierten Nutzer auf, mit ihren Profilbildern, Namen, Skills und Aktionen (Profil ansehen, private Nachricht senden). Über das Eingabefeld „Suche nach Skill“ können Sie die Liste filtern. Geben Sie einen Skill oder Teil davon ein (z.B. "Python") und klicken Sie auf Suchen. Es werden dann nur Nutzer angezeigt, die diesen Begriff in ihren hinterlegten Skills haben. So finden Sie schnell Personen mit bestimmten Fähigkeiten (z.B. Programmierkenntnissen).

Nutzer in der Nähe finden: Ebenfalls auf der Benutzer-Seite können Sie per Klick auf „Umkreis“ andere Nutzer in Ihrer geografischen Nähe ermitteln. Voraussetzung: Sie selbst haben Ihren Standort (Lat, Lng) im Profil gesetzt. Die Anwendung ruft dann die API /user/nearby auf, welche mithilfe der Haversine-Formel alle Nutzer innerhalb eines Radius von 30 km findet. Das Ergebnis wird direkt auf der Seite unterhalb des Suchformulars als Liste angezeigt – inklusive Entfernungsangabe in Kilometern zu jedem gefundenen Nutzer. So können Sie z.B. Teammitglieder in Ihrer Umgebung identifizieren. (Hinweis: Diese Funktion erfordert einen aktiven Login und den zuvor erwähnten JWT-Token im Browser, da der API-Endpunkt geschützt ist.)

Projekte und Aufgaben: Über den Menüpunkt Projekte gelangen Sie zur Projektverwaltung Ihres Teams. Hier sind alle Projekte aufgelistet, die von Teammitgliedern angelegt wurden. Zu jedem Projekt wird der Name und der Status angezeigt (bspw. In Progress oder Done). Sie können ein neues Projekt erstellen, indem Sie auf „Projekt anlegen“ klicken und einen Namen eingeben. In der Projekt-Detailansicht sehen Sie die Liste der dazugehörigen Tasks/Aufgaben. Für jedes Projekt können neue Aufgaben hinzugefügt werden („Task anlegen“), wobei Sie einen Titel, eine Beschreibung, einen Verantwortlichen (Teammitglied) und optional eine Deadline angeben können. Aufgaben erscheinen mit ihrem Titel, Status und ggf. zuständigem Benutzer in der Liste. Der Status einer Aufgabe kann per Klick geändert werden (z.B. von To Do auf Done, wenn erledigt) – hierzu gibt es Buttons oder Dropdowns neben der Aufgabe. Dieses einfache Projektmanagement-Feature ermöglicht es dem Team, gemeinsame Todos zu verfolgen und zu bearbeiten.

Dateiablage nutzen: Innerhalb eines Teams können Dateien zentral gespeichert werden. Über die Team-Seite oder direkt beim Chat finden Sie einen Bereich Dateiablage. Mit Durchsuchen/Datei auswählen können Sie eine Datei von Ihrem Rechner auswählen und hochladen. Alle hochgeladenen Dateien werden in einer Liste angezeigt – inkl. Dateiname, Upload-Datum und Uploader. Teammitglieder können die Dateien über einen Klick auf den Dateinamen herunterladen. Dieses Feature erleichtert den Austausch von Dokumenten, Bildern etc. im Team. Die Ablage ist teamweit sichtbar; es empfiehlt sich daher, nur für das Team relevante Dateien hochzuladen.

### Hinweise zur Weiterentwicklung

Diese Anwendung ist ein Prototyp, der im Rahmen eines Lernszenarios entstanden ist. Einige mögliche Erweiterungs- oder Verbesserungsansätze für zukünftige Versionen sind:

Echte Echtzeit-Kommunikation: Derzeit werden Chatnachrichten durch regelmäßiges Abfragen dargestellt. Durch Integration von WebSockets (z.B. via Flask-SocketIO) ließe sich ein in Echtzeit aktualisierter Chat umsetzen, inklusive Live-Statusanzeigen (Benutzer online/offline, „schreibt gerade…“ etc.). Ebenso könnten Benachrichtigungen bei neuen Nachrichten oder Team-Ereignissen in Echtzeit erscheinen.

Verbesserte Team-Verwaltung: Momentan kann ein Nutzer nur einem Team angehören. Künftige Versionen könnten Einladungslinks oder Team-Codes bereitstellen, um den Beitritt zu Teams nach der Registrierung zu erleichtern. Auch Rollen innerhalb des Teams (Admin/Member) und Berechtigungen (z.B. nur Team-Admin darf Mitglieder hinzufügen oder entfernen) wären denkbar.

Private Chats in Datenbank speichern: Die 1:1-Chats werden aktuell in einer JSON-Datei persistiert, was für den Prototyp ausreichend ist. Eine Weiterentwicklung sollte diese jedoch in ein eigenes Datenbankmodell (mit Beziehungen zu Usern) überführen, um Skalierbarkeit und Abfragefunktionen (z.B. anzeige der letzten Nachricht, ungelesene Nachrichten) zu verbessern.

Projektmanagement ausbauen: Das vorhandene Projekt- und Task-Feature ließe sich erweitern, z.B. mit Kommentarfunktionen pro Task, Dateien pro Task anhängen, Prioritäten, oder Kanban-ähnliche Boards. Eine Kalenderansicht für Deadlines oder eine Benachrichtigung bei nahendem Fälligkeitsdatum wären praktische Ergänzungen.

KI-Integration vertiefen: Die KI-Antworthilfe kann ausgebaut werden, etwa indem automatisch Antwortvorschläge erscheinen oder verschiedene Tonalitäten gewählt werden können. Zudem könnten KI-Features wie automatische Zusammenfassungen langer Chatverläufe oder das Vorschlagen von passenden Teammitgliedern basierend auf Skills hinzukommen.

Security & Deployment: Für den produktiven Einsatz sollten Sicherheitsmaßnahmen vertieft werden (z.B. Eingabefilter, Rate Limiting für APIs, Bild-Upload-Validierung). Auch die Konfiguration für unterschiedliche Umgebungen (Development vs. Production) und die Bereitstellung via WSGI-Server (z.B. Gunicorn) in der Cloud wären nächsinnvoll, inkl. eines Containerizations (Docker) für einfachere Deployments.
