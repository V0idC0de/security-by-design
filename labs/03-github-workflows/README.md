# 03 GitHub Workflows

- [03 GitHub Workflows](#03-github-workflows)
  - [Durchführung](#durchführung)
    - [1. Ordnerstruktur und Vorbereitung](#1-ordnerstruktur-und-vorbereitung)
    - [2. GitHub Login](#2-github-login)
    - [3. Repository erstellen](#3-repository-erstellen)
    - [4. Repository und Workflows überprüfen](#4-repository-und-workflows-überprüfen)
    - [5. Neuen Branch pushen](#5-neuen-branch-pushen)
    - [6. Pull Request erstellen](#6-pull-request-erstellen)
    - [7. GitHub Actions beobachten](#7-github-actions-beobachten)
    - [8. Fehlschlag auslösen](#8-fehlschlag-auslösen)
    - [9. Formatting-Workflow beobachten](#9-formatting-workflow-beobachten)
    - [10. Aufräumen](#10-aufräumen)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [1. Klone das Repository](#1-klone-das-repository)
    - [2. Baue den Container](#2-baue-den-container)
    - [3. Starten des Containers](#3-starten-des-containers)
    - [Existierenden Container verwenden](#existierenden-container-verwenden)
    - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In diesem Lab wird gezeigt, Arbeitsaufläuge in GitHub-Repositories mit integrierten **GitHub Workflows** automatisiert werden können,
um z.B. Secrets, potenziell gefährlichen Code und Formatierungsfehler zu finden, bevor sie in einen produktiven Branch gelangen.

> [!NOTE]
> Wenn keine Lab-Umgebung zur Verfügung gestellt wird, kann das Lab mit Terraform auch lokal ausprobiert werden.
> Eine Nutzungsanleitung zum lokalen Aufsetzen des Labs findet sich unter [Lokale Umgebung bauen](#lokale-umgebung-bauen).

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindest (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Ordnerstruktur und Vorbereitung

Untersuche den aktuellen Ordner und beachte den Unterordner `demo-workflows`.
Wechsle zur Vorbereitung in den `demo-workflows` Ordner und wirf einen Blick auf die vorbereiteten Dateien.

```bash
ls -l
cd demo-workflows
# Zeige gesamte Ordnerstruktur
tree -a demo-workflows
```

Diese Dateien werden gleich schrittweise als Commits in ein Git-Repository geschrieben.

### 2. GitHub Login

Folge den Schritten in [GitHub Login](/github-login.md).

### 3. Repository erstellen

```bash
cd demo-workflows
# Lokales Git Repository initialisieren
git init
# Ersten Commit ins Repository schreiben
git add sample.yaml .github/workflows/ci.yml
git commit -m "Initial Commit"
# Lokales Repository auf GitHub schreiben
gh repo create --private --source . --push
```

Folgt dem Link im angezeigten Text, um schnell zum erstellen Repository zu gelangen.

### 4. Repository und Workflows überprüfen

Navigiere zu deinem neu erstellten Repository und sieh dir die Struktur des Repositories an.
Anschließend, sieh dir den GitHub Workflow genauer er, der in `.github/workflows/ci.yml` konfiguriert ist.
Dieser Workflow wird ausgeführt, wenn ein neuer Pull Request im Repository geöffnet oder geupdated wird
(siehe Objekt `on:`).

In jedem Schritt des Workflows geben die Zeilen mit `run:` oder `uses:` an, welche Aktivität durchzuführen ist.
`run:` führt ein Kommendo in einer Shell direkt aus und `uses:` importiert eine fertige Aktion und führt sie aus,
wobei diese Action-Namen schlicht Repositories auf GitHub sind.

- **(Optional)** Versuche zu ermitteln, was diese einzelnen Schritte tun und welchen Zweck sie erfüllen.

> [!NOTE]
> Workflows werden inzwischen in vielen Plattformen in einfachen Konfigurationsdateien (oft in YAML) gespeichert.
> Das macht sie einfach als Teil des Repositories versionierbar.
> Diese Workflows können meist von vielen Dingen ausgelöst werden. Manuell, zeitgesteuert oder bei Events wie
> neuen Commits, Pull Requests, Releases, uvm. Somit lassen sich repetitive Aufgaben gut automatisieren.

### 5. Neuen Branch pushen

Füge dem Repository neue Inhalte hinzu, um einen Pull Request zu erstellen.
Erstelle dazu einen neuen Branch `add-python` und committe `sample.py`.

```bash
git checkout -b add-python
git add sample.py
git commit -m "Python Code"
```

Lade den neuen Branch auf das Remote-Repository in GitHub hoch.

```bash
git push
```

### 6. Pull Request erstellen

Navigiere auf GitHub zu deinem Repository.
Erstelle einen Pull Request, um den neuen Branch in den `main` Branch zu mergen.

> [!NOTE]
> Falls für einen Branch kürzlich Commits hochgeladen wurden, weist GitHub üblicherweise im Repository mit einem gelben Banner darauf hin.
> Der Pull Request kann dann auch mit einem Klick auf den grünen Button **"Compare & pull request"** erstellt werden.
> **Falls das gelbe Banner nicht erscheint**, nutze die folgende Methode, die immer funktioniert.

1. Klicke auf **"Pull requests"** in deinem Repository
2. Klicke auf **"New pull request"**
3. Wähle die erstellte Branch als Source und `main` als Target
4. Erstelle den Pull Request

### 7. GitHub Actions beobachten

Nach dem Erstellen des Pull Requests:

1. Beobachte, wie automatisch ein GitHub Workflow startet. **Es kann ca. 5-10 Sekunden dauern, bis die Workflows im Pull Request registriert werden.**
2. Klicke die Workflows über dem **Merge pull request**-Button an und beobachte die ausgeführten Schritte,
die in der Datei `.github/workflows/ci.yml` aus [Schritt 4](#4-repository-und-workflows-überprüfen) beschrieben werden.

> [!NOTE]
> GitHub und andere Plattformen verfügen über Einstellungen, die erfolgreiche Pipelines zur Voraussetzung für
> einen Merge machen. Somit können z.B. bestandene Tests erzwungen werden, bevor Änderungen in einen produktiven Branch gelangen.
> Wäre dies konfiguriert, ließe sich der **"Merge pull request"** Button nicht betätigen, bis die Pipelines fehlerlos abschließen.

### 8. Fehlschlag auslösen

Da eine der Pipelines korrekte Formatierung überprüft, kann ein Fehlschlag des Workflows einfach demonstriert werden.
Verändere `sample.yaml` wie folgt:

```bash
nano sample.yaml
```

- Verändere die Zeile des Attributs `hello:`, sodass nach dem `:` noch mehrere Leerzeichen folgen, z.B. `hello:   Security by Design`. Dies ist ein Formatierungsfehler, der zwar keinen Fehler produziert, aber einem Linter auffällt.
- Entferne die erste Zeile, die `---` enthält. Dies signalisiert des Beginn eines YAML-Dokuments und sollte vorhanden sein. Ein Linter wird ggf. darauf hinweisen.

Speichere die Änderungen mit `STRG + S` und verlasse den Editor mit `STRG + X`.

Lade die Änderungen als Commit in das Remote-Repository auf GitHub:

```bash
git add sample.yaml
git commit -m "Format error"
git push
```

### 9. Formatting-Workflow beobachten

Beobachte auf der Website des Pull Requests die automatische erneute Ausführung der Workflows.
Diese wurden vom neu hochgeladenen Commit ausgelöst.

Klicke den Workflow `Repository Content CI / Format Check (Python & YAML) (pull_request)` und beobachte die Ausführung.

Nachdem der Workflow fehlgeschlagen ist, aktualisiere die Seite und beachte dann oben die **Annotations**-Anzeige.
Hier können Schritte besondere Ergebnisse hervorheben. `yamllint` zeigt uns die eben eingebauten Formatierungsfehler klar auf.

### 10. Aufräumen

Dies waren alle Schritte des Labs.
Um kein verwaistes Repository zurückzulassen, lösche das Repository, z.B. mit der GitHub CLI.

```bash
gh repo delete
```

Bestätige die Löschung durch Eingabe des Repository-Namens.

### Abschluss

In diesem Lab hast du gesehen, wie CI-Pipelines (Continuous Integration) genutzt werden können, um repetitive Aufgaben, wie Formatierung und andere Prüfungen, automatisiert durchzuführen.
Neben GitHub Workflows gibt es noch andere Tools, um derartige CI-Pipelines aufzusetzen, wie **GitLab CI**, **Travis CI**, uvm.

## Lokale Umgebung bauen

Dieses Lab kann mit Docker selbst nachvollzogen und durchgearbeitet werden.
Voraussetzung ist eine Installation von [`docker`](https://docs.docker.com/engine/install/) (empfohlen)
ODER eine lokale Installation von [`GitHub CLI`](https://github.com/cli/cli#installation) (**beachte den untenstehenden Hinweis!**).

> [!NOTE]
> In diesem Lab werden keine besonderen Programme außer `GitHub CLI` genutzt, daher kann es auch ohne Docker
> genutzt werden. GitHub CLI muss dann lokal verfügbar sein.
> Einige wenige `git`-Kommandos aus den Anweisungen (z.B. `git push`) könnten weitere Parameter benötigen,
> da die `lab-homedir/.gitconfig`-Datei nicht vorkonfiguriert wurde. Sie ist nicht nötig und nimmt nur einige
> Konfigurationen und Parameter für Kommandos vorweg.
> Nutze diese Variante nur, wenn du mit Git-Einstellungen umgehen und eventuelle Fehler selbst beheben kannst.

### 1. Klone das Repository

```bash
git clone <repository-url>
cd security-by-design/labs/03-github-workflows
```

### 2. Baue den Container

```bash
docker build -t labs/03-github-workflows .
```

### 3. Starten des Containers

```bash
docker run -it --name github-workflows --hostname github-workflows labs/03-github-workflows
```

### Existierenden Container verwenden

Falls der Container bereits existiert:

```bash
docker start -i github-workflows
```

### Container löschen/zurücksetzen

```bash
docker rm github-workflows
```
