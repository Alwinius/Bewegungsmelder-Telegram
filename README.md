
# Bewegungsmelder Telegram Bot

### Unterschied Polling - WebHook
Wenn der Bot im polling Modus betrieben wird, ruft er regelmäßig die API
von Telegram auf, um an ihn gesendete Nachrichten zu bekommen. Dies passiert
aber so häufig, dass die Verzögerungen kaum spürbar sind.  
Im Webhook Modus kontaktieren Telegram-Server den Bot an der WebhookUrl
um ihn über neue Nachrichten zu informieren. Dafür ist also ein extern per HTTPS
erreichbarer Server nötig, mit entsprechend konfiguriertem Reverse-Proxy, der
HTTPS-Verschlüsselung übernimmt und Anfragen an den Port des Bots weiterleitet.  
Der Webhook Modus wird aktiviert, falls in der `config.ini` eine WebhookUrl
angegeben ist.

## Anforderungen
- entweder Docker
- oder Python 3
- Linux, Windows wurde nicht getestet

## Setup normal
1. config.ini mit config.ini.example erstellen
2. virtualenv installieren und Abhängigkeiten mit pip install -r requirements.txt installieren
3. `python main.py daemon` ausführen
4. um sofort alle Termine von der Website abzurufen, kann einmalig
`python main.py scrape` ausgeführt werden. Dies erfolgt automatisch alle 5h.

Tipp: zu Testzwecken kann der Daemon mit dem Tool screen ausgeführt werden,
damit er auch nach dem Schließen der SSH-Verbindung zum Server weiter läuft.
Für stabilen Betrieb sollte aber ein SystemD service angelegt werden oder anderweitig
sichergestellt werden, dass der Bot immer läuft und erreichbar ist.

## Setup docker-compose lokal bauen
1. config.ini mit config.ini.example erstellen, hierbei sollte der Port auf 8080 gestellt bleiben
2. `docker-compose -f docker-compose-local.yml build` ausführen, um das Docker image zu bauen
3. entweder `${PORT}` durch den gewünschten externen Port ersetzen oder eine .env Datei mit folgendem Inhalt erstellen:
`PORT=1234`
Damit wird der Port 8080 auf diesen Port des hosts weitergeleitet und so der Betrieb per Webhook möglich.
4. Und abschließend den Container mit `docker-compose up -d` starten.

Wenn der Bot nur per polling betrieben werden soll, ist keine Portweiterleitung nötig.
Der entsprechende Bereich kann aus der `docker-compose-local.yml` also komplett
auskommentiert oder gelöscht werden. Nur wenn `${PORT}` referenziert ist, aber
nirgendwo definiert ist, kommt es zu einem Fehler.
