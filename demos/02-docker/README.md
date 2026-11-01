# Docker

Die Demo zeigt die Isolation von Prozessen und Dateisystemen in Docker-Containern sowie die
Persistenz von Daten in Docker-Volumes.

## Voraussetzungen

- Docker muss installiert sein ([Installation](https://docs.docker.com/engine/install/)).
- `htop` muss auf dem Host installiert sein.
- Der Host läuft unter Linux.
- Der Benutzer hat Zugriff auf den Docker-Daemon.

## Durchführung

> [!WARNING]
> Die Demo greift auf das Docker-Datenverzeichnis `/var/lib/docker` zu. Sie sollte deshalb nur in
> einer dafür vorgesehenen Lernumgebung ausgeführt werden.

Drei Terminal-Panels öffnen (Links, oben rechts, unten rechts).

- Panel 1 bleibt auf dem Host
- Panel 2 wird zur Shell für Container A
- Panel 3 wird zur Shell für Container B bzw. Host-Ansicht

In Panel 1 das Skript `monitor.sh` mit folgendem Befehl ausführen:

```bash
watch -n 1 ./monitor.sh
```

In Panel 2 und 3 das Image festlegen. Der Digest fixiert die verwendete Version:

```bash
IMAGE='alpine:3.23.5@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40'
```

### 1. Getrennte Dateisystemansichten

Auf dem Host die Root-Ansicht anzeigen:

```bash
ls -li /
```

Im zweiten Panel einen Container in einer Shell starten und dieselbe Abfrage ausführen:

```bash
docker run --name demo-fs --entrypoint /bin/sh -it "$IMAGE"
ls -li /
```

Beide Ansichten verwenden denselben Linux-Kernel, aber der Container sieht eine eigene Root-Ansicht.
Die erste Spalte von `ls -lai` enthält die Inode-Nummer.

Im Container eine Datei und zwei Links anlegen:

```bash
cd /home
touch original.txt
ln -s original.txt soft.txt
ln original.txt hard.txt
```

Die drei Verzeichniseinträge mit ihren Inodes anzeigen:

```bash
ls -lai original.txt hard.txt soft.txt
```

Der Hardlink und `original.txt` haben dieselbe Inode und zeigen damit auf dieselbe Datei. Der
Symlink hat eine eigene Inode und enthält nur den Verweis auf `original.txt`.

```bash
TEST_FILE=$(find /var/lib/docker -type f -name 'original.txt' -print -quit)
echo "$TEST_FILE"
ls -li "$TEST_FILE"
```

Die Dateien sind auch außerhalb des Container-Dateisystens auf dem Host sichtbar.

Den Container nun verlassen und entfernen.

Im Container `exit` und auf dem Host anschließend

```bash
docker container rm demo-fs
```

> [!NOTE]
> In folgenden Schritte geschieht dies automatisch beim Verlassen durch das `--rm`-Flag beim Kommando `docker run`.

### 2. Prozessisolation

Einen Container in einer Shell starten und seine Prozesssicht anzeigen:

```bash
docker run --rm --name demo-proc --entrypoint /bin/sh -it "$IMAGE"
ps -a
```

Im Container einen langlebigen Prozess starten:

```bash
sleep infinity
```

Im Host-Panel `htop` starten:

```bash
sudo htop
# Alternativ als einzelne Query
ps -eo user=,pid=,args= | grep infinity
sudo kill <PID>
```

Der Prozess ist im Host-`htop` sichtbar. Die Host-PID ablesen und mit `F9` -> `SIGKILL (9)` beenden.
Die Container-Shell wird dadurch wieder aktiv. Der Container nutzt den Host-Kernel, besitzt aber einen
eigenen Process Namespace.

Container verlassen:

```bash
exit
```

### 3. Unabhängige Container-Dateisysteme

Für diesen Abschnitt Panel 1 als Host-Panel sowie Panel 2 für Container A und Panel 3 für Container B
verwenden. Zwei Container aus demselben Image interaktiv starten.

In Panel 2 Container A starten:

```bash
docker run --name demo-a --entrypoint /bin/sh -it "$IMAGE"
```

In Panel 3 Container B starten:

```bash
docker run --name demo-b --entrypoint /bin/sh -it "$IMAGE"
```

In Container A eine Datei anlegen:

```bash
touch /tmp/from-a.txt
```

In Container B nach derselben Datei suchen:

```bash
ls -l /tmp/from-a.txt
```

Der Befehl schlägt fehl: Beide Container stammen aus demselben Image, haben aber getrennte
beschreibbare Dateisysteme.

Container A verlassen:

```bash
exit
```

In Panel 1 Container A entfernen:

```bash
docker container rm demo-a
```

In Panel 2 mit demselben Image eine neue Container-A-Instanz interaktiv starten:

```bash
docker run --name demo-a --entrypoint /bin/sh -it "$IMAGE"
```

Die Datei aus dem entfernten Container ist auch in der neuen Instanz nicht vorhanden:

```bash
ls -l /tmp/from-a.txt
```

Damit ist der beschreibbare Container-Layer an den Lebenszyklus der Container-Instanz gebunden.

Die Container-Shells verlassen und Container B in Panel 1 entfernen:

Panel 2:

```bash
exit
```

Panel 3:

```bash
exit
```

Panel 1:

```bash
docker container rm demo-b
```

### 4. Persistenz mit einem Volume

Ein Volume unabhängig vom Container-Lebenszyklus erstellen:

```bash
docker volume create demo-volume
docker volume ls
```

In Panel 2 einen Container mit dem Volume unter `/data` starten:

```bash
docker run --name demo-vol-a -v demo-volume:/data -it "$IMAGE" /bin/sh
```

Im Container eine Datei im Volume anlegen:

```bash
touch /data/volume.txt
```

Eine zweite Datei im Container-Layer anlegen:

```bash
touch /tmp/container.txt
ls -l /data/volume.txt /tmp/container.txt
```

Den Container verlassen und dadurch stoppen:

```bash
exit4
```

In Panel 1 prüfen, dass der Container gestoppt ist:

```bash
docker ps -a
```

In Panel 2 dieselbe Container-Instanz wieder an die Shell anbinden:

```bash
docker start -ai demo-vol-a
```

Beide Dateien sind nach dem Stoppen und Starten noch vorhanden:

```bash
ls -l /data/volume.txt /tmp/container.txt
```

Den Container erneut verlassen:

```bash
exit
```

In Panel 1 den Container entfernen:

```bash
docker container rm demo-vol-a
```

In Panel 2 eine neue Instanz mit demselben Volume starten:

```bash
docker run --name demo-vol-b -v demo-volume:/data -it "$IMAGE" /bin/sh
```

Die Datei im Volume bleibt erhalten, aber die Datei aus dem Container-Layer ist verschwunden:

```bash
ls -li /data /tmp
```

Das Volume ist vom Contain  er-Lebenszyklus getrennt.
Ebenso lässt sich hier ebenso die Gleichheit der INode-IDs zeigen:

```bash
cd /var/lib/docker/volumes/demo-volume
ls -liR
```

Den neuen Container verlassen:

```bash
exit
```

In Panel 1 alle Ressourcen entfernen:

```bash
docker container rm demo-vol-b
docker volume rm demo-volume
```
