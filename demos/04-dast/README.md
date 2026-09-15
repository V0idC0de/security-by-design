# Dynamische Anwendungssicherheit mit OWASP ZAP

Diese Demo zeigt, wie der OWASP Juice Shop als Docker Container gestartet und seine API mit einem
DAST-Scan (Dynamic Application Security Testing) von einem zweiten Container aus untersucht wird.

## Voraussetzungen

- Docker muss installiert sein ([Installation](https://docs.docker.com/engine/install/)).
- Linux wird als Betriebssystem verwendet.
- Der verwendete Benutzer benötigt Berechtigungen für den Docker-Daemon.

## Durchführung

> [!WARNING]
> Führe automatisierte Scans nur gegen Anwendungen aus, für die du eine ausdrückliche Erlaubnis
> hast. Der OWASP Juice Shop ist eine absichtlich verwundbare Anwendung und sollte ausschließlich in
> einer dafür vorgesehenen Lernumgebung betrieben werden.

### 1. Juice Shop als Container starten

Starte den Juice Shop im Hintergrund und veröffentliche seinen Port `3000` auf dem Host:

```bash
docker run --rm \
  --name juice-shop \
  --publish 127.0.0.1:3000:3000 \
  bkimminich/juice-shop:v20.2.0@sha256:8739101ade29358abb5469ee66ae78e582c97ed0a5543a4ad102e5fa5193526b
```

Zeige den laufenden Container:

```bash
docker ps
sudo netstat -tulpn | grep -i docker
```

Die Anwendung ist nun im Browser unter [http://127.0.0.1:3000](http://127.0.0.1:3000) erreichbar.
Alternativ kann die Erreichbarkeit auf dem Host mit `curl` geprüft werden:

```bash
curl http://127.0.0.1:3000
```

### 2. OpenAPI-Spezifikation des Juice Shops prüfen

Der Juice Shop stellt seine API-Beschreibung im OpenAPI-/Swagger-Format bereit. Prüfe zunächst, ob
die Spezifikation erreichbar ist:

```bash
curl http://127.0.0.1:3000/api-docs/
```

Die URL zur OpenAPI-Spezifikation wird anschließend als Ziel für ZAP verwendet.

### 3. Juice-Shop-API mit OWASP ZAP scannen

Der ZAP-Container soll das Netzwerk-Interface des Hosts verwenden. Mit `--network host` erhält der
Container keinen eigenen Netzwerk-Namespace. `localhost` innerhalb des ZAP-Containers bezeichnet
dadurch denselben Netzwerk-Stack wie `localhost` auf dem Host. Starte den ZAP-API-Scan deshalb in
einem zweiten Container mit `--network host`.

Der Parameter `-f openapi` weist ZAP an, das Ziel nach einer OpenAPI Spec abzusuchen,
um daraus die verfügbaren API-Endpunkte auszulesen und gezielt zu scannen.
Der HTML-Bericht `zap-report.html` wird im aktuellen Verzeichnis gespeichert
und ist dank des gemounteten `./`-Verzeichnisses auch nachträglich auf dem Host verfügbar.

```bash
docker run --rm \
  --network host \
  --volume "./:/zap/wrk:rw" \
  zaproxy/zap-stable:2.17.0@sha256:781a2bdaea47324e7bab583e2263f21d257b0aee61ed51521a5be45f5f5081ef \
  zap-api-scan.py \
    -f openapi \
    -t http://127.0.0.1:3000/api-docs/openapi.json \
    -r zap-report.html
```

Während des Scans zeigt ZAP die gefundenen Warnungen und die geprüften API-Endpunkte im Terminal an.
Nach Abschluss kann der Bericht `zap-report.html` im Browser geöffnet werden.

<!-- markdownlint-disable MD028 -->

> [!NOTE]
> Der **Juice Shop** enthält primär logische Fehler, die von DAST-Tools nur schwer gefunden werden können.
> Für ein Beispiel mit der von **PortSwigger** bereitgestellten Applikation GinAndJuice-Shop können auch andere
> Findings demonstriert werden, dieser dauert jedoch deutlich länger.
> Ca. 25 Minuten für einen Full Scan und ~5 Minuten, wenn der `ajax-spider` aus den Jobs (`FullScanGinNJuiceAuth.yaml`) entfernt wird.

> [!WARNING]
> Das untenstehende Kommando greift die Seite `https://ginandjuice.shop` im Internet an.
> PortSwigger stellt sie dafür bereit, doch vermeide exzessive Angriffe gegen den Host!

<!-- markdownlint-enable MD028 -->

```bash
curl -O https://raw.githubusercontent.com/zaproxy/community-scripts/f9cb362056f6c613ee60364e119ad4cab2fd0dd5/other/af-plans/FullScanGinNJuiceAuth.yaml
docker run --rm \
  --network host \
  -v "$(pwd):/zap/wrk/:rw" \
  zaproxy/zap-stable:2.17.0@sha256:781a2bdaea47324e7bab583e2263f21d257b0aee61ed51521a5be45f5f5081ef \
  zap.sh \
    -cmd \
    -autorun \
    wrk/FullScanGinNJuiceAuth.yaml
```

### 4. Scan-Ergebnisse nachvollziehen

Vergleiche die Warnungen aus dem Terminal mit dem HTML-Bericht:

```bash
ls -l
python -m http.server
# Besuche http://127.0.0.1:8000, um den Report im Browser zu sehen
```

DAST findet nur Schwachstellen, die während des Scans erreichbar und ausführbar sind.
Nicht aufgerufene Funktionen werden dementsprechend nicht untersucht.

### 5. Container beenden

Stoppe den Juice Shop nach der Demo:

```bash
# Falls `--detach`/`-d` beim Starten nicht gesetzt war, kann der Container mit Strg+C beendet werden.
# Ansonsten führe das folgende Kommando aus.
docker stop juice-shop
```

Da der Container mit `--rm` gestartet wurde, wird er nach dem Stoppen automatisch entfernt.
