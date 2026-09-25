# Docker Images bauen und ausführen

Diese Demo zeigt, wie ein Docker Image aus einem `Dockerfile` gebaut und anschließend als Container
ausgeführt wird. Dabei werden außerdem Port-Weiterleitungen und Umgebungsvariablen betrachtet.

## Voraussetzungen

- Docker muss installiert sein ([Installation](https://docs.docker.com/engine/install/)).
- Docker Compose muss verfügbar sein (`docker compose`).
- Linux wird als Betriebssystem verwendet.

## Durchführung

> [!NOTE]
> Führe die folgenden Befehle aus dem Verzeichnis `demos/03-build-docker-image` aus. Dort liegen
> `app.py`, `Dockerfile` und `docker-compose.yaml`.

### 1. Anwendung und Image untersuchen

1. Zeige `app.py`. Die Anwendung startet einen kleinen HTTP-Server und verwendet die
    Umgebungsvariable `GREETED` für die Antwort.
2. Zeige das `Dockerfile` und erläutere die Schritte zum Erstellen des Images:
    Basis-Image auswählen, Anwendung kopieren, nicht-root Benutzer verwenden und den Port festlegen.

### 2. Image bauen

```bash
docker build -t demos/docker-building:latest -t demos/docker-building:v1.0.0 .
```

Zeige das neu erstellte Image:

```bash
docker images
```

### 3. Container mit Docker Compose starten

```bash
docker compose up -d
docker ps
```

Die Compose-Datei veröffentlicht den Container-Port `8000` auf dem Host-Port `9999`.
Ein Zugriff auf den unveröffentlichten Container-Port über den Host-Port `8000` schlägt daher fehl:

```bash
curl http://127.0.0.1:8000
```

Der veröffentlichte Port liefert dagegen die erwartete Antwort:

```bash
curl http://127.0.0.1:9999
```

Zeige bei Bedarf die von Docker eingerichtete Weiterleitung:

```bash
sudo netstat -tulpn | grep -i docker
```

### 4. Container stoppen und erneut starten

Beobachte den Dienst in einem zweiten Terminal-Panel:

```bash
watch -n 0.5 curl http://127.0.0.1:9999
```

Stoppe und starte den Compose-Dienst im ersten Panel:

```bash
docker compose stop
docker compose start
```

Container lassen sich dadurch sehr schnell stoppen und wieder starten.

### 5. Umgebungsvariable verändern

Verändere `docker-compose.yaml`, sodass `GREETED` nicht mehr gesetzt wird, und starte den Dienst
erneut:

```bash
docker compose up -d
curl http://127.0.0.1:9999
```

Die Antwort lautet nun `Hello Students!`. In `app.py` gibt es keinen Standardwert für `GREETED`.
Der Wert kommt deshalb aus dem `Dockerfile`, in dem `ENV GREETED=Students` gesetzt ist.

### 6. Container ohne Compose ausführen

Stoppe und entferne zuerst den Compose-Container:

```bash
docker compose down
```

Starte das Image anschließend direkt mit `docker run` und setze die Umgebungsvariable explizit:

```bash
docker run --rm --publish 9999:8000 --env GREETED=Course demos/docker-building:latest
```

Zeige in einem zweiten Terminal-Panel den laufenden Container:

```bash
docker ps
```
