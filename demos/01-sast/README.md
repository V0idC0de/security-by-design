# SAST

Einfache Demonstration von SAST und Secret Scanning Tools anhand des bekanntes `juice-shop` Repositories von **OWASP**,
das absichtliche Fehler enthält, um als Übungsziel für Penetration Tests und Security Tools zu fungieren.

## Kurzanleitung

### 1. Repository klonen

Projekt in /tmp/juice-shop herunterladen

```bash
git clone -b v20.1.1 --single-branch https://github.com/juice-shop/juice-shop /tmp/juice-shop
```

### 2. Secrets scannen mit betterleaks

Zuerst betterleaks Container starten

```bash
docker run --user "$(id -u)" -w /tmp/juice-shop -v /tmp/juice-shop:/tmp/juice-shop:ro --hostname betterleaks --rm -it --entrypoint /bin/bash ghcr.io/betterleaks/betterleaks:v1.7.3@sha256:4522fe41a2d22f9bf9b4100c20488b79a5af5c37abc8f3d0cdccdcc47dac3523
```

Secrets in aktuellen Dateien finden

```bash
betterleaks dir -v
```

Secrets in Git-Historie finden (zeigt auch gelöschte Secrets)

```bash
betterleaks git -v --git-workers=16
```

### 3. Schwachstellen mit semgrep prüfen

Semgrep Container starten

```bash
docker run --user "$(id -u)" -w /tmp/juice-shop -v /tmp/juice-shop:/tmp/juice-shop:ro --hostname semgrep --rm -it --entrypoint /bin/bash semgrep/semgrep:1.172.0@sha256:65dcd4408adda7c183a6b4550cb1e9b19f7f627a6fbb7e0559bd466bedc44d7b
```

JavaScript Code vollständig scannen

```bash
semgrep scan --lang=js .
```

Spezifische Datei mit "tainted input" Vulnerabilities prüfen

```bash
semgrep scan --lang=js routes/search.ts
```
