# 02 Pre-Commit

- [02 Pre-Commit](#02-pre-commit)
  - [Durchführung](#durchführung)
    - [1. Betrachte das Setup im Container](#1-betrachte-das-setup-im-container)
    - [2. Untersuche das Git-Repository](#2-untersuche-das-git-repository)
    - [3. YAML-Datei committet](#3-yaml-datei-committet)
    - [4. `pre-commit` installieren und aktivieren](#4-pre-commit-installieren-und-aktivieren)
    - [5. `pre-commit` konfigurieren](#5-pre-commit-konfigurieren)
    - [6. Neue Dateien committen](#6-neue-dateien-committen)
    - [7. Fehler korrigieren](#7-fehler-korrigieren)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [1. Klone das Repository](#1-klone-das-repository)
    - [2. Baue den Container](#2-baue-den-container)
    - [3. Starten des Containers](#3-starten-des-containers)
    - [Existierenden Container verwenden](#existierenden-container-verwenden)
    - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In diesem Lab wird ein Beispiel-Repository mit Python- und YAML-Code bereitgestellt, der absichtlich Formatierungsfehler und Klartext-Secrets im Quellcode enthält.
Ziel des Labs ist es, verschiedene Tools wie einen Code-Linter, einen YAML- und Python-Formatter sowie einen Secret Scanner für Git-Repositories einzusetzen, um diese Probleme zu erkennen.

Die Tools werden über eine pre-commit-Konfigurationsdatei (`.pre-commit-config.yaml`) eingebunden, sodass sie bei jedem Commit automatisch ausgeführt werden.
So siehst du, wie sich Sicherheits- und Qualitätsprüfungen automatisiert in den Entwicklungsprozess integrieren lassen.

Falls `pre-commit` einen Beanstandung im Code findet, gibt das Tool einen Fehler zurück, was zu einem Abbruch des Commits führt - gerade rechtzeitig, um die Fehler zu beheben.

> [!NOTE]
> Wenn keine Lab-Umgebung zur Verfügung gestellt wird, kann das Lab mit Docker auch lokal ausprobiert werden.
> Eine Nutzungsanleitung zum lokalen Aufsetzen des Labs findet sich unter [Lokale Umgebung bauen](#lokale-umgebung-bauen).

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindet (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Betrachte das Setup im Container

```bash
# `-a`: Listet alle Dateien, auch unsichtbare Dateien, deren Name mit `.` beginnt
# `-I ".git": Nimmt den Ordner `.git` von der Liste aus, da er viele unleserliche, hier unwichtige Dateien enthält.
tree -a -I '.git'

# `ls -lR` listet ebenfalls rekursiv, `tree` zeigt allerdings die Datei-Hierarchy etwas schicker
```

> [!NOTE]
> Beachte den Ordner `lab-repository`, der unser Git-Repository für diese Übung ist.
> Ebenso die im aktuellen Verzeichnis (noch nicht im Repository!) befindliche `.pre-commit-config.yaml`,
> auf die wir zurückkommen werden.
> `.gitconfig` sind die globalen Einstellungen für Git.

### 2. Untersuche das Git-Repository

```bash
# Wechsele ins `lab-repository` (drücke ggf. `TAB` um Ordnernamen zu vervollständigen)
# "cd lab" genügt um den Ordnernamen mit der <TAB>-Taste zu vervollständigen
cd lab-repository

# Zeige die bisherigen Commits im Repository
git log

# Zeige noch nicht committete Dateien und Änderungen
git status
```

> [!NOTE]
> Das Repository hat bereits einen Commit, sowie neue Dateien, die noch nicht committet wurden.

### 3. YAML-Datei committet

```bash
git add sample.yaml
# Der Inhalt der Commit-Message, die `-m` setzt, ist hier nicht wichtig
git commit -m 'Add YAML'
# Bestätige, dass der Commit jetzt in der Git-History sichtbar ist
git log
```

> [!NOTE]
> Die YAML-Datei hat Formatierungsfehler, d.h. eine schlecht formatierte Datei wurde committet. Das soll in Zukunft nicht mehr passieren.

### 4. `pre-commit` installieren und aktivieren

```bash
# Installiert das pre-commit Paket für den Benutzer via Python Package Manager
pip install pre-commit==4.3.0

# Schreibt im aktuellen Git-Repository das `pre-commit`-Python-Tool in den Git Hook für `pre-commit`,
# sodass es vor Commits ausgeführt wird.
pre-commit install

# Output: pre-commit installed at .git/hooks/pre-commit
```

> [!NOTE]
> Git-Hooks führen beliebige Skripte oder Befehle aus. Das Python-Tool `pre-commit`, das via `pip` installiert wurde,
> enthält ein Programm, das die Datei `.pre-commit-config.yaml` im Repository sucht, interpretiert und die Anweisungen ausführt.
> YAML ist natürlich keine direkt ausführbare Sprache, doch sie ist hervorragend lesbar.
> Pythons `pre-commit` macht aus der YAML-Datei konkrete Befehle.

### 5. `pre-commit` konfigurieren

```bash
# Kopiere die vorbereitete `.pre-config-config.yaml` ins Repository, um `pre-commit` zu konfigurieren
cp ~/.pre-commit-config.yaml .

# Betrachte Inhalte der Konfiguration
batcat .pre-commit-config.yaml
```

> [!NOTE]
> Die Konfiguration sollte uns einige Tools zum Formatieren und Linten zeigen, sowie die bekannten Git-Secret-Scanner.

### 6. Neue Dateien committen

> [!WARNING]
> Die erste Ausführung von `pre-commit` in einem Repository via `git commit` dauert wegen der Ersteinrichtung hier ~1 Minute.
> Alle folgenden Ausführunge sind deutlich schneller, da die Umgebung wiederverwendet wird.

```bash
# Commit der schlecht formatierten YAML-Datei rückgängig machen
git reset --soft HEAD~1

# Inhalt der `sample.yaml` und `sample.py` überprüfen.
# Achte auf die "AKIA..." Keys für AWS und die schlechte Formatierung in `sample.yaml`.
batcat sample.yaml sample.py

# Alle Dateien im aktuellen Verzeichnis zum geplanten Commit hinzufügen
git add .

# Commit durchführen - wir erwarten, dass `pre-commit` die konfigurierten Schritte durchführt.
git commit -m 'Add code'
# Der Inhalt der Commit-Message, die `-m` setzt, ist hier nicht wichtig
```

### 7. Fehler korrigieren

```bash
# Korrekturen betrachten (benutze Pfeiltaste-Hoch, um durch vorherige Kommandos zu scrollen)
# YAML ist jetzt einheitlich eingerückt und überschüssiger Whitespace wurde aus dem Python-Code entfernt.
batcat sample.yaml sample.py

# Secret aus der Python-DAtei entfernen.
# Nutze entweder das untenstehende Kommando, oder erledige es manuell mit "nano" oder "vi".
sed -i '/AKIA/d' sample.py

# Verifiziere, dass das Secret entfernt ist
batcat sample.py

# Korrekturen der pre-commit Hooks zum Commit hinzufügen
git add .

# Commit erneut versuchen - bei Fehler die Note-Box unten beachten!
git commit -m 'Add code'

# Commit in der Git-History bestätigen
git log
```

> [!NOTE]
> Sollte einer der Hooks erneut einen Formatierungsfehler o.Ä. finden, hat er ihn wahrscheinlich auch schon behoben.
> Wiederhole dann einfach `git add .` und `git commit -m 'Add code'`, um die Korrekturen hinzuzufügen und erneut zu committen.

### Abschluss

In diesem Lab hast du die Anwendung von **pre-commit Hooke** gesehen und wie diese einfach über das Tool `pre-commit` genutzt werden können.
Du hast außerdem den **Secret Scanner "TruffleHog"** genutzt, um automatisiert Secret im Code aufzuspüren und ihren Commit zu verhindern.

So können Security-Tools ohne Mehraufwand in den Entwicklungsprozess integriert werden. `pre-commit` kann dabei auch Aufgaben übernehmen,
die nicht direkt der Security dienen und ist daher auch für die sonstige Entwicklung ein nützliches Werkzeug.

Aufgeräumt werden muss in diesem Lab nichts.

## Lokale Umgebung bauen

Dieses Lab kann mit Docker selbst nachvollzogen und durchgearbeitet werden.
Voraussetzung ist eine Installation von `docker` ([Installation](https://docs.docker.com/engine/install/)).

### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

### 2. Baue den Container

> [!WARNING]
> Stelle sicher, dass du dich in diesem Verzeichnis `labs/02-pre-commit` im Repository befindest,
> bevor du `docker build` ausführst! Für alle anderen `docker`-Befehle ist das Verzeichnis egal.

```bash
# Überspringe dieses Kommando, falls du schon in diesem Unterordner bist
cd security-by-design/labs/02-pre-commit
```

```bash
docker build -t labs/02-pre-commit .
```

### 3. Starten des Containers

```bash
docker run -it --name pre-commit --hostname pre-commit labs/02-pre-commit
```

> [!NOTE]
> `docker run` öffnet eine Shell innerhalb des Containers, die für das Lab genutzt werden kann.
> Wird das Terminal geschlossen, die Shell mit `CTRL + D`, `exit`, o.Ä. verlassen, stoppt der Container.
> Er wird allerdings nicht gelöscht und kann weiterverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden))

### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container erneut zu betreten:

```bash
docker start -ai pre-commit
```

### Container löschen/zurücksetzen

Falls bereits ein Container mit diesem Namen existiert, kann er vorher entfernt werden.
Dies kann verwendet werden, um mit dem Lab neu zu starten.

```bash
docker rm -f pre-commit
```

Nach Ausführung des zweiten Befehls befindet man sich direkt in einer Shell im Container und kann dort alle Übungen durchführen.
