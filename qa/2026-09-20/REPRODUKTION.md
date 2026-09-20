# Tests wiederholen

Die Programme schreiben Testdaten. Sie sind ausschließlich für die isolierte Testkopie auf **3100/5101** bestimmt. Die eigentliche Anwendung auf **3000/5001** bleibt davon getrennt.

Voraussetzungen: Projekt-`.venv`, Google Chrome unter `/Applications/Google Chrome.app`, Node und Playwright. Die Testdaten müssen die Demo-Nutzer Bob, Alice und Carla enthalten.

Die archivierten JSON-Dateien und Screenshots dokumentieren den Lauf vom 20.09.2026. Ein erneuter Lauf überschreibt die jeweiligen Ergebnisse; bei Bedarf den Ordner vorher kopieren.

Aus dem Projektverzeichnis eine neue Kopie erzeugen:

```sh
.venv/bin/python qa/2026-09-20/prepare-test-copy.py /private/tmp/collab-qa-repeat
npm install --prefix /private/tmp/collab-qa-tools playwright
.venv/bin/python /private/tmp/collab-qa-repeat/serve.py
```

Dafür müssen die Testports 3100 und 5101 frei sein. Das letzte Kommando läuft als Server und wird mit Ctrl+C beendet. Die ursprünglichen Server auf 3000/5001 brauchen dafür nicht beendet zu werden.

In einem zweiten Terminal, wieder aus dem Projektverzeichnis, nacheinander:

```sh
node qa/2026-09-20/browser-audit.cjs pages-chat
node qa/2026-09-20/browser-audit.cjs workflows
node qa/2026-09-20/browser-audit.cjs edgecases
.venv/bin/python qa/2026-09-20/api-audit.py
COLLAB_QA_COPY=/private/tmp/collab-qa-repeat .venv/bin/python qa/2026-09-20/extra-checks.py
```

`workflows` legt Projekte/Tasks an; `edgecases` verwendet deren IDs aus `workflow-ids.json`. Daher diese Reihenfolge beibehalten. Während der Browser-Phasen keine anderen Änderungen in der Testkopie vornehmen.

Das Testprogramm läuft nach einzelnen fehlgeschlagenen Erwartungen weiter. „FAIL“ wird absichtlich protokolliert, damit alle Bereiche untersucht werden können. Ein erfolgreicher Prozessabschluss bedeutet daher nicht, dass alle Funktionen bestanden haben. Maßgeblich sind die Ergebnisdateien.

Zwei Registrierung-Folgeprüfungen in `workflows` setzen eine erfolgreiche Bildregistrierung voraus. Bei deren bekanntem Fehler sind sie nicht unabhängig aussagekräftig und wurden im Bericht ausgeschlossen. Die separaten Fälle in `edgecases` prüfen Registrierung ohne Bild, Login und Duplikate unabhängig.

Der Paralleltest sendet in zehn Runden jeweils zwei Nachrichten gleichzeitig. Er sichert und restauriert anschließend ausschließlich die Nachrichten-Datei der Testkopie. Das Ausmaß des reproduzierten Datenverlusts ist von der Ausführungsreihenfolge abhängig und kann zwischen Läufen variieren.

Der HTML-Test setzt lediglich ein DOM-Attribut als Ausführungsnachweis. Er liest keine fremden Daten aus und sendet nichts an externe Dienste. Die Testnachricht bleibt als Beleg in der isolierten Chatdatei; nachfolgend wird eine harmlose Textnachricht als letzte Vorschau gesendet.
