# Building and Running Docker Images

Demonstration für das Bauen und Ausführen von Docker Images.

## Vorbereitung

- Docker muss installiert sein
- Linux ist das Betriebssystem

## Durchführung

1. Zeige die `app.py`, die unsere App darstellt
2. Zeige den `Dockerfile` und erläutere die Schritte zum Build-Prozess
3. `docker build -t demos/images:latest .`
4. `docker images` zum zeigen des neu gebauten Image
5. `docker compose up` zum Starten des Containers
6. `docker ps` zum zeigen des laufenden Containers
7. Auf dem Host: `curl http://127.0.0.1:8000` - es demonstriert, dass die Interfaces des Containers, speziell sein `localhost` nicht identisch mit dem des Hosts ist.
8. `sudo netstat -tulpn | grep -i docker` um den `docker-proxy` zu zeigen
9. `curl http://127.0.0.1:9999` (wie in `docker-compose.yaml` spezifiziert) zeigt dann die erwartete Antwort
10. `docker stop` auf die Container-Instanz stoppt den Prozess -> Seite nichtmehr erreichbar
11. `watch -n 0.5 curl http://127.0.0.1:9999` um den Container in einem Panel zu beobachten und die Startgeschwindigkeit zu zeigen
12. `docker start` startet die Instanz wieder - Container lassen sich sehr schnell stoppen und starten
13. Verändere `docker-compose.yaml`, sodass `GREETED` fehlt und führe `docker compose up` nochmal aus
14. Erneutes `curl http://127.0.0.1:9999`, um `Hello Students` zu zeigen
    1. Verweis auf das fehlen eines Standardwertes in `app.py`, sodass dieser Standardwert für die Umgebungsvaraible aus dem `Dockerfile` kommt
15. Container stoppen und entfernen
16. `docker run --rm --publish 9999:8000 --env GREETED Course demos/images:latest` und `docker ps` im anderen Panel, um die Ausführung ohne `docker-compose.yaml` zu zeigen
