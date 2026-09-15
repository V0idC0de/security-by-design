# Docker

Demonstration einer Docker Installation und wie diese Container auf Filesystem-Ebene zur Verfügung stellt.

## Voraussetzungen

- Docker muss installiert sein
- Linux wird als Betriebssystem verwendet werden

## Durchführung

1. 2 Panels im Terminal nebeneinander, beide als `root` (bzw. User mit Berechtigungen für den `docker` Daemon)
   1. **Panel 1:** `cd /var/lib/docker`
   2. **Panel 2:** `docker run --hostname container-linux --rm -it --entrypoint /bin/sh alpine:3.23.5@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40`
2. Auf beiden Panels `ls -lai /` zur Darstellung der verschiedenen Root-Verzeichnisse
   1. Beachte die erste Spalte, die `ls -i` liefert - sie zeigt die iNodes in denen die Daten physisch liegen. Diese sind verschieden
3. **[Panel 2]:** `cd home` und dann `echo hello world > test.txt`, um eine Datei im Container zu erstellen
4. **[Panel 1]:** `find /var/lib/docker -name 'test.txt'` zum schnellen Aufspüren der Datei
   1. In das Verzeichnis der Datei wechseln und sturkturelle Gleichheit zum Container-Ordner zeigen
5. **[Panel 1]:** `echo hello students > test.txt` ausführen, um die Datei vom Host-System aus zu überschreiben
6. **[Panel 2]:** `cat test.txt` demonstriert, dass der Inhalt im Container dem auf dem Host-System entspricht
7. Auf beiden Panels `ls -lai` ausführen und aufzeigen, dass die Dateien tatsächlich auf dieselben Daten/iNodes zeigen
   1. Hier ein Hinweis auf Softlinks und Hardlinks
