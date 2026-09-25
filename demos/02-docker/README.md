# Docker

Die Demo demonstriert die Prozess- und Dateisystemisolation von Docker-Containern sowie die
Persistenz von Daten in Docker-Volumes.

## Voraussetzungen

- Docker muss installiert sein ([Installation](https://docs.docker.com/engine/install/)).
- `htop` muss auf dem Host installiert sein.
- Der Host läuft unter Linux.
- Der Benutzer hat Zugriff auf den Docker-Daemon.

## Durchführung

> [!WARNING]
> Für diese Demo wird direkt auf das Docker-Datenverzeichnis `/var/lib/docker` des Hosts zugegriffen.
> Die Schritte sollten deshalb nur in einer dafür vorgesehenen Lernumgebung ausgeführt werden.

### Variablen setzen

In jedem Panel setzen. Der Digest fixiert die verwendete Image-Version:

```bash
IMAGE='alpine:3.23.5@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40'
```

### 1. Dateisystem und Prozesse

Zuerst die unterschiedliche Root-Ansicht bei gemeinsamem Host-Kernel demonstrieren. Host-Root und
Container-Root vergleichen; bei `ls -lai` auf die Inode-Spalte achten. Die Strukturen ähneln sich,
die Root-Ansichten sind jedoch getrennt.

Panel 1:

```bash
cd /var/lib/docker
ls -lai /
```

Panel 2:

```bash
docker run --name demo-fs --entrypoint /bin/sh -it "$IMAGE"
ls -lai /
cd /home
echo hello world > test.txt
ls -lai test.txt
```

Docker setzt das Container-Dateisystem aus mehreren Image-Layern und einem beschreibbaren Container-
Layer zusammen. Copy-on-Write vermeidet vollständige Kopien unveränderter Daten. Die im Container
unter `/home` sichtbare Datei auf dem Host in der Docker-Datenstruktur suchen und überschreiben:

```bash
TEST_FILE=$(find /var/lib/docker -type f -name 'test.txt' -print -quit)
ls -lai "$TEST_FILE"
echo hello students > "$TEST_FILE"
```

Panel 2:

```bash
cat /home/test.txt
ls -lai /home/test.txt
exit
```

Panel 2 beenden und den Container entfernen:

```bash
docker rm demo-fs
```

Der neue Inhalt ist im Container sichtbar, weil dessen Mount-Ansicht die geänderte Layer-Datei nutzt.
Die Inode-Werte der unterschiedlichen Dateisystemansichten müssen nicht identisch sein.

Für die Prozessisolation Host- und Container-Sicht parallel anzeigen: Der Host soll den Container-
Prozess sehen, während der Container nur seine eigene Namespace-Sicht erhält.

Panel 1, Host:

```bash
htop
```

Panel 2, Container:

```bash
docker run --name demo-proc --entrypoint /bin/sh -it "$IMAGE"
ps -a
```

Im Container einen langlebigen Prozess starten, damit derselbe Prozess in beiden Sichten eindeutig
identifiziert werden kann:

```bash
sleep infinity
```

Ohne `sleep infinity` abzubrechen zu Panel 1 wechseln. Der Prozess erscheint im laufenden Host-`htop`.
Seine Host-PID ablesen und mit `F9` -> `SIGKILL (9)` -> `Enter` beenden. Alternativ in einem weiteren
Host-Panel ausführen:

```bash
kill -9 <host-pid>
```

Die Shell im Container wird dadurch wieder aktiv. Beide Ansichten verwenden denselben Linux-Kernel;
die Container-Prozesssicht bleibt auf den eigenen Namespace begrenzt.

Panel 2:

```bash
exit
docker rm demo-proc
```

### 2. Ephemeres Dateisystem

Zuerst die Lebensdauer des beschreibbaren Container-Layers von der Container-Instanz unterscheiden:
Datei anlegen, Container stoppen und starten und die Datei erneut prüfen. Nach dem Entfernen mit
demselben Namen neu erstellen und feststellen, dass die Datei nicht übernommen wird.

Panel 2:

```bash
docker run --name demo-ephemeral -it "$IMAGE" /bin/sh
echo temporary data > /home/ephemeral.txt
ls -lai /home/ephemeral.txt
exit
```

Panel 1:

```bash
docker ps -a
docker start -ai demo-ephemeral
ls -lai /home/ephemeral.txt
exit
docker rm demo-ephemeral
docker run --name demo-ephemeral -it "$IMAGE" /bin/sh
ls -lai /home/ephemeral.txt
exit
docker rm demo-ephemeral
```

Stop und Start erhalten das beschreibbare Layer; erst `docker rm` entfernt die Container-Instanz samt
Layer. Persistente Daten benötigen deshalb ein Volume oder einen anderen persistenten Speicher.

### 3. Persistenz mit Volume

Ein Volume demonstriert die Trennung von Container-Lebenszyklus und Daten. Volume außerhalb des
Containers erstellen, Datei darin anlegen, Container entfernen und das Volume in eine neue Instanz
mounten. Die Inode im Container mit der Host-Datei vergleichen.

Panel 1:

```bash
docker volume create demo-volume
docker volume ls
```

Panel 2:

```bash
docker run --name demo-vol-a -it -v demo-volume:/data "$IMAGE" /bin/sh
touch /data/persistent.txt
ls -lai /data/persistent.txt
exit
```

Panel 1:

```bash
docker rm demo-vol-a
VOLUME_PATH=$(docker volume inspect -f '{{.Mountpoint}}' demo-volume)
ls -lai "$VOLUME_PATH/persistent.txt"
```

Panel 2:

```bash
docker run --name demo-vol-b -it -v demo-volume:/data "$IMAGE" /bin/sh
ls -lai /data/persistent.txt
```

Die Datei bleibt nach Entfernen und Neuerstellen des Containers erhalten, weil sie im Volume und nicht
im Container-Layer liegt. Das Volume ist vom Container-Lebenszyklus getrennt.

### 4. Gemeinsames Volume

Ein gemeinsames Volume demonstriert Datenaustausch und Mount-Rechte. Das Volume bleibt im
Schreibcontainer gemountet; parallel einen weiteren Container mit demselben Volume im Read-only-Modus
starten.

Panel 3, im Read-only-Container:

```bash
docker run --name demo-vol-ro -it -v demo-volume:/data:ro "$IMAGE" /bin/sh
watch -n 1 'ls -la /data'
```

Panel 2, im Schreibcontainer:

```bash
touch /data/shared.txt
```

Während `watch` läuft, erscheint die Datei nach dem `touch` sofort im Read-only-Container. Damit wird
der gemeinsame Datenbestand sichtbar. Mit `Ctrl+C` beenden und anschließend den Schreibschutz prüfen:

```bash
touch /data/forbidden.txt
```

Der Schreibversuch muss fehlschlagen.

Panel 3:

```bash
exit
```

Panel 2:

```bash
exit
```

Panel 1:

```bash
docker rm demo-vol-ro demo-vol-b
docker volume inspect demo-volume
docker volume rm demo-volume
```

## Show Notes

### Vorbereitung

Zwei Terminal-Panels öffnen: Panel 1 bleibt auf dem Host, Panel 2 wird zur Container-Shell. Für die
Volume-Demo ein drittes Panel bereithalten. Die Panels benötigen `root` oder Zugriff auf den
Docker-Daemon.

In jedem Panel ausführen:

```bash
IMAGE='alpine:3.23.5@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40'
```

`docker run` erstellt einen Container aus dem Image und startet den angegebenen Prozess. Beim ersten
Start die Syntax bewusst einfach halten: `--entrypoint /bin/sh` erzwingt die Shell als Einstiegspunkt;
danach `-it` als interaktives Terminal erklären. `-v` mountet ein Volume in den Container. Ohne `--rm`
muss der Container nach dem Verlassen explizit entfernt werden.

### 1. Dateisysteme und Inodes

Zuerst den physischen Speicherort der Docker-Layer auf dem Host öffnen. Dadurch lässt sich die Datei
aus der isolierten Container-Sicht später einer Host-Datei zuordnen.

Panel 1 in das Docker-Datenverzeichnis wechseln:

```bash
cd /var/lib/docker
```

Mit dem Host-Root beginnen. Diese Ausgabe dient als Referenz für die spätere Root-Ansicht im
Container:

```bash
ls -lai /
```

Panel 2 startet den Container direkt in der Shell. Die Reihenfolge stellt den Einstiegspunkt vor den
Terminaloptionen heraus:

```bash
docker run --name demo-fs --entrypoint /bin/sh -it "$IMAGE"
```

Dieselbe Abfrage im Container ausführen. Die ähnliche Struktur zeigt das gemeinsame Linux-Dateisystem;
die getrennte Root-Ansicht zeigt die Isolation:

```bash
ls -lai /
```

Die Verzeichnisstruktur ähnelt dem Host, `/` ist jedoch eine eigene Root-Ansicht. Die erste Spalte von
`ls -lai` enthält die Inode-Nummer.

Im Container eine Datei anlegen. Sie erscheint zunächst nur in dieser Mount-Ansicht:

```bash
cd /home
echo hello world > test.txt
ls -lai test.txt
```

Docker kombiniert Image-Layer mit einem beschreibbaren Container-Layer zu einem virtuellen
Dateisystem. Copy-on-Write verhindert dabei vollständige Kopien unveränderter Daten. In Panel 1 die
Container-Datei in der Docker-Datenstruktur suchen:

```bash
TEST_FILE=$(find /var/lib/docker -type f -name 'test.txt' -print -quit)
ls -lai "$TEST_FILE"
```

Den gefundenen Pfad mit `/home` im Container vergleichen. Die Datei ist im Container sichtbar, liegt
auf dem Host jedoch in einer von Docker verwalteten Layer-Struktur. Die Isolation erzeugt eine andere
Sicht auf diese Daten, nicht zwingend eine vollständige Kopie.

Die gefundene Datei im Host-Panel überschreiben:

```bash
echo hello students > "$TEST_FILE"
```

Zurück in Panel 2:

```bash
cat /home/test.txt
ls -lai /home/test.txt
```

Der neue Inhalt ist sofort sichtbar. Das zeigt, dass die Container-Sicht die geänderte Layer-Datei
nutzt. Die Inode-Werte beider Dateisystemansichten müssen nicht identisch sein.

Container-Shell verlassen:

```bash
exit
```

Der Container wurde mit einem festen Namen gestartet und kann daher gezielt entfernt werden:

```bash
docker rm demo-fs
```

### 2. Prozesse und Host-Sicht

Jetzt Host und Container direkt gegenüberstellen, nicht zwei Container. Der Host soll den Prozess des
Containers sehen, während der Container nur seine eigene Prozessansicht erhält. Panel 1 zeigt den Host:

```bash
htop
```

Panel 2 startet genau einen Container:

```bash
docker run --name demo-proc --entrypoint /bin/sh -it "$IMAGE"
```

Im Container alle sichtbaren Prozesse anzeigen. Die reduzierte Liste ist die erwartete Wirkung der
Process-Namespace-Isolation:

```bash
ps -a
```

Die Containeransicht enthält nur wenige Prozesse. Im Host-`htop` sind die Containerprozesse sichtbar,
weil sie auf dem Host-Kernel laufen.

Im Container einen dauerhaften Prozess starten. Ein eindeutig benannter Prozess macht die gemeinsame
Sichtbarkeit in Host und Container nachvollziehbar:

```bash
sleep infinity
```

`sleep infinity` nicht abbrechen, sondern zu Panel 1 wechseln. Der Prozess erscheint im laufenden
Host-`htop`. Dort die PID ablesen und mit `F9` -> `SIGKILL (9)` -> `Enter` beenden. Alternativ in einem
weiteren Host-Panel ausführen:

```bash
kill -9 <host-pid>
```

Die Shell im Container wird dadurch wieder aktiv. Dass ein Host-Signal den Containerprozess beendet,
zeigt: Containerprozesse sind reguläre Hostprozesse mit zusätzlicher Kernel-Isolation.

Panel 2 aufräumen:

```bash
exit
docker rm demo-proc
```

### 3. Ephemeres Dateisystem

Panel 2 startet einen benannten Container. Der Name wird später für `start` und `rm` wiederverwendet:

```bash
docker run --name demo-ephemeral -it "$IMAGE" /bin/sh
```

Im Container Datei anlegen und Inode anzeigen:

```bash
echo temporary data > /home/ephemeral.txt
ls -lai /home/ephemeral.txt
```

Die Datei liegt jetzt im beschreibbaren Layer dieser Container-Instanz. Nach dem Stop bleibt dieses
Layer erhalten, solange die Instanz existiert. Shell verlassen:

```bash
exit
```

Nach `exit` ist der Container gestoppt, aber nicht entfernt. Panel 1 zeigt ihn deshalb noch in der
Container-Liste:

```bash
docker ps -a
```

Mit `docker start` dieselbe Container-Instanz erneut an die Shell anbinden. Damit wird gezeigt, dass
Stop und Start das beschreibbare Layer nicht löschen:

```bash
docker start -ai demo-ephemeral
```

Die Datei ist nach Stop und Start weiterhin vorhanden:

```bash
ls -lai /home/ephemeral.txt
exit
```

Jetzt den Container wirklich entfernen und mit exakt demselben Namen neu erstellen. Der gleiche Name
bezeichnet eine neue Instanz und stellt keine Daten wieder her:

```bash
docker rm demo-ephemeral
docker run --name demo-ephemeral -it "$IMAGE" /bin/sh
ls -lai /home/ephemeral.txt
```

Die Datei fehlt jetzt, weil die neue Instanz wieder aus dem Basis-Image startet. Der Name identifiziert
keine persistente Datenablage. Shell verlassen und aufräumen:

```bash
exit
docker rm demo-ephemeral
```

Wichtige Daten dürfen daher nicht ausschließlich im Container-Dateisystem liegen.

### 4. Volume und Persistenz

Panel 1 erstellt ein Volume unabhängig vom Container-Lebenszyklus:

```bash
docker volume create demo-volume
docker volume ls
```

Panel 2 startet den ersten Container mit dem Volume:

```bash
docker run --name demo-vol-a -it -v demo-volume:/data "$IMAGE" /bin/sh
```

Im Container Datei anlegen und Inode anzeigen:

```bash
touch /data/persistent.txt
ls -lai /data/persistent.txt
```

Die Datei liegt im Volume, nicht im beschreibbaren Container-Layer. Shell verlassen:

```bash
exit
```

Panel 1 entfernt nur den Container und prüft die Datei direkt auf dem Host:

```bash
docker rm demo-vol-a
VOLUME_PATH=$(docker volume inspect -f '{{.Mountpoint}}' demo-volume)
ls -lai "$VOLUME_PATH/persistent.txt"
```

Die Datei bleibt erhalten, weil das Volume den Container-Lebenszyklus überlebt. Der Host-Vergleich
zeigt, dass Container und Host auf denselben Volume-Inhalt zugreifen.

Panel 2 startet eine neue Container-Instanz mit demselben Volume:

```bash
docker run --name demo-vol-b -it -v demo-volume:/data "$IMAGE" /bin/sh
```

Im neuen Container prüfen:

```bash
ls -lai /data/persistent.txt
```

Datei und Inode sind wieder vorhanden. Das Volume persistiert Daten über Container-Instanzen hinweg.

### 5. Gemeinsamer und schreibgeschützter Mount

Panel 2 bleibt in `demo-vol-b`. Panel 3 startet parallel denselben Volume-Mount read-only:

```bash
docker run --name demo-vol-ro -it -v demo-volume:/data:ro "$IMAGE" /bin/sh
watch -n 1 'ls -la /data'
```

`watch` führt `ls -la /data` jede Sekunde erneut aus. Währenddessen in Panel 2 eine Datei im Volume
anlegen:

```bash
touch /data/shared.txt
```

Die Datei erscheint unmittelbar in Panel 3. Mit `Ctrl+C` `watch` beenden und im Read-only-Container
den Schreibschutz prüfen:

```bash
touch /data/forbidden.txt
```

Der Befehl schlägt fehl, weil der Mount mit `:ro` keine Änderungen zulässt. Der Read-only-Container
kann die vom Schreibcontainer erzeugten Daten dennoch lesen.

Panel 3 verlassen:

```bash
exit
```

Panel 2 verlässt den Schreibcontainer:

```bash
exit
```

Panel 1 räumt auf:

```bash
docker rm demo-vol-ro demo-vol-b
docker volume ls
docker volume inspect demo-volume
docker volume rm demo-volume
```

Das Löschen der Container löscht das extern angelegte Volume nicht. Erst `docker volume rm` entfernt
auch die persistenten Daten. Der schnelle Containerstart verdeutlicht abschließend den Unterschied zur
VM: Docker startet Prozesse mit spezieller Kernel-Konfiguration; eine VM muss ein eigenes
Betriebssystem booten.
