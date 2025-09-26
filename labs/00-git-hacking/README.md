# 00 Git Hacking mit `.git` Ordner

- [00 Git Hacking mit `.git` Ordner](#00-git-hacking-mit-git-ordner)
  - [Durchführung](#durchführung)
    - [1. Zugriff auf die Beispiel-Webseite](#1-zugriff-auf-die-beispiel-webseite)
    - [2. Zugriff auf das Config-Verzeichnis testen](#2-zugriff-auf-das-config-verzeichnis-testen)
    - [3. Zugriff auf das `.git`-Verzeichnis prüfen](#3-zugriff-auf-das-git-verzeichnis-prüfen)
    - [4. Repository mit Githacker rekonstruieren](#4-repository-mit-githacker-rekonstruieren)
    - [5. Analyse der wiederhergestellten Daten](#5-analyse-der-wiederhergestellten-daten)
    - [6. Suche nach Secrets mit Truffle Hog](#6-suche-nach-secrets-mit-truffle-hog)
    - [7. Code-Analyse mit Bandit](#7-code-analyse-mit-bandit)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [1. Klone das Repository](#1-klone-das-repository)
    - [2. Baue den Container](#2-baue-den-container)
    - [3. Starten des Containers](#3-starten-des-containers)
    - [Existierenden Container verwenden](#existierenden-container-verwenden)
    - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In diesem Lab bekommst du einen Beispiel-Webserver, der eine Hauptseite ausliefert und den Zugriff aufs `config`-Verzeichnis blockiert. Das simuliert einen Webserver, der Quellcode und andere Dateien vor direktem Zugriff schützt. Ein kritischer Fehler ist aber, dass das `.git`-Verzeichnis beim Setup nicht entfernt oder geschützt wurde. Dadurch kann das komplette Repository rekonstruiert werden. Ziel des Labs ist es, diese Schwachstelle auszunutzen, das Repository mit dem Tool `githacker` wiederherzustellen, nach Secrets zu suchen und den Quellcode auf Schwachstellen zu checken.

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindest (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Zugriff auf die Beispiel-Webseite

```bash
curl http://localhost:8000
```

Die Startseite wird angezeigt und informiert dich, dass Dateien im `config`-Verzeichnis nicht zugänglich sind.

### 2. Zugriff auf das Config-Verzeichnis testen

```bash
curl http://localhost:8000/config
```

Der Zugriff wird verweigert – der Webserver blockiert das Verzeichnis wie erwartet.

### 3. Zugriff auf das `.git`-Verzeichnis prüfen

```bash
curl http://localhost:8000/.git/config
```

Die Ausgabe zeigt die Git-Konfiguration – das `.git`-Verzeichnis ist zugänglich!

### 4. Repository mit Githacker rekonstruieren

```bash
githacker --url http://localhost:8000 --output-folder git-hack
```

Das Tool lädt alle relevanten Dateien aus dem `.git`-Verzeichnis und stellt das Repository im Ordner `git-hack` wieder her.

> [!NOTE]
> `githacker` zeigt unter den Log-Meldungen auch einige Errors – das ist nicht schlimm.
> Die treten zum Beispiel auf, weil `githacker` versucht, Branch-Namen und ähnliche Dinge zu erraten.

### 5. Analyse der wiederhergestellten Daten

```bash
cd git-hack
# Name des Unterordners herausfinden
ls
cd <unterordner>
ls -la
git log
```

Das Repository ist komplett wiederhergestellt, inklusive Commit-Historie und Quellcode.

```bash
batcat *
batcat config/*
```

Mit `batcat` kannst du Quellcode und Konfigurationsdateien anschauen. Es sind keine sensiblen Daten im Klartext auffindbar.

> [!NOTE]
> `batcat` ist eine schickere Version von `cat`. Z.B. zeigt es die Dateien mit Syntax-Highlighting im Terminal an. Du kannst natürlich auch jedes andere Tool verwenden.

### 6. Suche nach Secrets mit Truffle Hog

```bash
trufflehog git file://.
```

Truffle Hog durchsucht die komplette Git-Historie nach Secrets. Es wird ein Secret gefunden, das in einem früheren Commit stand, aber nicht mehr im aktuellen Code ist.

> [!WARNING]
> Secrets, die einmal im Git-Verlauf landen, sind nie wirklich gelöscht! Nur ein "force push" kann Commits entfernen, was aber meist auf geschützten Branches nicht erlaubt ist und mit Vorsicht genutzt werden sollte. Das Entfernen von versehentlich eingecheckten Secrets ist daher schwierig.

### 7. Code-Analyse mit Bandit

```bash
# Lässt `bandit` rekursiv alle Dateien nach Problemen untersuchen
bandit -r .
```

Bandit analysiert den Python-Code und findet eine offensichtliche SQL-Injection-Schwachstelle, die durch unsichere String-Konkatenation entsteht.

> [!INFO]
> Hier können in der Praxis natürlich beliebige andere Analysen folgen, z.B. Suche nach "versteckten" Endpunkten.
> Denke selbst kurz darüber nach, welche Möglichkeiten es für einen Angreifer eröffnet, den Quellcode zur Verfügung zu haben.
> Zwar ist **Security by Obscurity** keine gute Strategie, doch den Quellcode zu kennen ermöglicht einem Angreifer sehr viel effektivere Suche
> nach Angriffsmöglichkeiten, wenn es die Ergebnisse nicht schon direkt mitliefert (z.B. Klartext-Secrets). Daher sollte Quellcode gut geschützt werden.

### Abschluss

In diesem Lab hast du gesehen, wie ein offenes `.git`-Verzeichnis genutzt werden kann, um ein komplettes Repository samt Historie wiederherzustellen.
Mit den Tools konntest du Secrets aus der Historie extrahieren und Schwachstellen im Quellcode finden.
Das zeigt, wie wichtig ein sauberes Server-Setup und der Schutz sensibler Verzeichnisse ist – auch präventiv, falls doch mal ein `.git`-Ordner ins Deployment gerät (Security in Depth).

## Lokale Umgebung bauen

Du kannst das Lab mit Docker selbst ausprobieren.
Voraussetzung ist eine Installation von `docker` ([Installation](https://docs.docker.com/engine/install/)).

### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

### 2. Baue den Container

> [!WARNING]
> Stell sicher, dass du dich im Verzeichnis `labs/00-git-hacking` im Repository befindest,
> bevor du `docker build` ausführst! Für alle anderen `docker`-Befehle ist das Verzeichnis egal.

```bash
# Überspringe dieses Kommando, falls du schon in diesem Unterordner bist
cd security-by-design/labs/00-git-hacking
```

```bash
docker build -t labs/00-git-hacking .
```

### 3. Starten des Containers

```bash
docker run -it --name git-hacking --hostname git-hacking labs/00-git-hacking
```

> [!NOTE]
> `docker run` öffnet eine Shell im Container, die du fürs Lab nutzen kannst.
> Wenn du das Terminal schließt oder die Shell mit `CTRL + D`, `exit` o.Ä. verlässt, stoppt der Container.
> Er wird aber nicht gelöscht und kann weiterverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden)).

### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container nochmal zu betreten:

```bash
docker start -ai git-hacking
```

### Container löschen/zurücksetzen

Falls schon ein Container mit diesem Namen existiert, kannst du ihn vorher entfernen.
Das ist praktisch, wenn du das Lab neu starten willst.

```bash
docker rm -f git-hacking
```

Nach dem zweiten Befehl bist du direkt in einer Shell im Container und kannst alle Übungen machen.
