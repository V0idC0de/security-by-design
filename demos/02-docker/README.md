# Docker

Diese Demo zeigt, wie Docker Container auf Dateisystemebene bereitstellt und wie das Dateisystem
eines Containers mit dem des Docker-Hosts zusammenhängt.

## Voraussetzungen

- Docker muss installiert sein ([Installation](https://docs.docker.com/engine/install/)).
- Linux wird als Betriebssystem verwendet.
- Der verwendete Benutzer benötigt Berechtigungen für den Docker-Daemon.

## Durchführung

> [!WARNING]
> Für diese Demo wird direkt auf das Docker-Datenverzeichnis `/var/lib/docker` des Hosts zugegriffen.
> Die Schritte sollten deshalb nur in einer dafür vorgesehenen Lernumgebung ausgeführt werden.

### 1. Container starten

Öffne zwei Terminal-Panels nebeneinander. Verwende in beiden Panels `root` oder einen Benutzer mit
ausreichenden Berechtigungen für den Docker-Daemon.

```bash
# Panel 1: Docker-Datenverzeichnis des Hosts
cd /var/lib/docker
```

```bash
# Panel 2: Shell im Container
docker run --hostname container-linux --rm -it --entrypoint /bin/sh \
  alpine:3.23.5@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40
```

### 2. Dateisysteme vergleichen

Führe in beiden Panels den folgenden Befehl aus:

```bash
ls -lai /
```

Die erste Spalte zeigt die Inodes, unter denen die Dateien physisch gespeichert sind. Die Root-
Verzeichnisse des Hosts und des Containers sind dabei verschieden.

### 3. Datei im Container anlegen

Führe im Container folgende Befehle aus:

```bash
cd /home
echo hello world > test.txt
```

Suche die Datei anschließend im Docker-Datenverzeichnis des Hosts:

```bash
find /var/lib/docker -name 'test.txt'
```

Wechsle in das gefundene Verzeichnis und vergleiche seine Struktur mit dem Verzeichnis im Container.

### 4. Datei vom Host aus verändern

Überschreibe die Datei im Host-Panel:

```bash
echo hello students > test.txt
```

Lies sie anschließend im Container-Panel aus:

```bash
cat test.txt
```

Der Inhalt im Container entspricht nun dem Inhalt auf dem Host. Führe in beiden Panels erneut
`ls -lai` aus und vergleiche die Inodes. Die Beobachtung lässt sich als Demonstration für Softlinks und
Hardlinks verwenden.
