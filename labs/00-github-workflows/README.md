# 00 GitHub Workflows

- [00 GitHub Workflows](#00-github-workflows)
  - [Durchführung](#durchführung)
    - [1. Ordnerstruktur und Vorbereitung](#1-ordnerstruktur-und-vorbereitung)
    - [2. Repository erstellen](#2-repository-erstellen)
      - [2.1. GitHub-Token konfigurieren](#21-github-token-konfigurieren)
      - [2.2. Terraform ausführen](#22-terraform-ausführen)
    - [3. Repository und Workflows überprüfen](#3-repository-und-workflows-überprüfen)
    - [4. Pull Request erstellen](#4-pull-request-erstellen)
    - [5. GitHub Actions beobachten](#5-github-actions-beobachten)
    - [6. Pull Request mergen](#6-pull-request-mergen)
    - [7. Aufräumen](#7-aufräumen)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [Lokale Umgebung mit Docker](#lokale-umgebung-mit-docker)
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

Untersuche den aktuellen Ordner und beachte den Unterordner `terraform`.
Wechsle zur Vorbereitung in den `terraform` Ordner.

```bash
ls -l
cd terraform
```

### 2. Repository erstellen

Für ein möglichst einfaches Setup wird in diesem Lab **Terraform** eingesetzt, um das Repository und alle Einstellungen
automatisiert aufzusetzen. Wie **Terraform** genau funktioniert, wird in anderen Labs beleuchtet.
Für dieses Lab genügt es zu wissen, dass die folgenden Schritte durchgeführt werden:

1. GitHub-Token zur Durchführung von Schritten im eigenen GitHub-Konto wird konfiguriert
2. Terraform wird ausgeführt, was die folgenden Dinge automatisch tut
   1. Repository wird erstellt
   2. Dateien werden im Repository platziert
   3. Neuer Branch mit einer neuen Datei wird erstellt

#### 2.1. GitHub-Token konfigurieren

Falls du noch kein GitHub-Token für die Durchführung von Labs hast, folge den Schritten in [GitHub PAT erstellen](/GitHub-PAT.md),
um eines zu erzeugen. Lege es dann mit den folgenden Schritten in der Laborumgebung ab.

```bash
cp github-pat.auto.tfvars.json.sample github-pat.auto.tfvars.json
nano github-pat.auto.tfvars.json
```

Trage das Token als Wert für das JSON-Feld ein, speichere mit `Strg + S` und verlasse den Editor mit `Strg + X`
(andere Editoren können natürlich auch genutzt werden).

#### 2.2. Terraform ausführen

Führe die folgenden Kommandos aus, um Terraform vorzubereiten und das Repository aufbauen zu lassen:

```bash
terraform init
terraform apply
```

Bestätige die geplanten Änderungen von Terraform mit `yes`.

> [!NOTE]
> Terraform erstellt ein neues Repository in deinem GitHub-Account mit Beispieldateien und einem Workflow.
> Die Repository-Inhalte werden aus dem `repository-content/` Verzeichnis übernommen.

Bei einem Fehler, wende ggf. folgenden Fix an.

> [!ERROR]
> Der Fehler `Error: Provider produced inconsistent final plan` kann, sollte er auftreten, wahrscheinlich durch erneutes Ausführen von `terraform apply`
> behoben werden. Möglicherweise wurde das Repository nach der Löschung zu schnell wieder erstellt.

### 3. Repository und Workflows überprüfen

Navigiere zu deinem neu erstellten Repository auf [GitHub.com](https://github.com/) und untersuche:

- die hochgeladenen Dateien im Repository
- die Branches, insb. den neuen Branch
- (Optional) den GitHub Actions Workflow in `.github/workflows/ci.yml`

### 4. Pull Request erstellen

Erstelle einen Pull Request, um den neuen Branch in den `main` Branch zu mergen.

> [!NOTE]
> Falls für einen Branch kürzlich Commits hochgeladen wurden, weist GitHub üblicherweise im Repository mit einem gelben Banner darauf hin.
> Der Pull Request kann dann auch mit einem Klick auf den grünen Button **"Compare & pull request"** erstellt werden.
> Ansonsten nutze die folgende Methode, die immer funktioniert.

1. Klicke auf **"Pull requests"** in deinem Repository
2. Klicke auf **"New pull request"**
3. Wähle die erstellte Branch als Source und `main` als Target
4. Erstelle den Pull Request

### 5. GitHub Actions beobachten

Nach dem Erstellen des Pull Requests:

1. Beobachte, wie automatisch ein GitHub Workflow startet. **Es kann ca. 5-10 Sekunden dauern, bis die Workflows im Pull Request registriert werden.**
2. Beachte auch, dass der **"Merge pull request"**-Button sich nicht klicken lässt, da die Workflows für den Merge **Voraussetzung** sind.
3. (Optional) Klicke die Workflows über dem **Merge pull request**-Button an und beobachte die ausgeführten Schritte,
die in der Datei `.github/workflows/ci.yml` aus [Schritt 3](#3-repository-und-workflows-überprüfen) beschrieben werden.

### 6. Pull Request mergen

Nachdem die Workflows erfolgreich abgeschlossen sind, kann der **Merge pull request**-Button geklickt werden. Führe den Merge durch.

### 7. Aufräumen

Um kein verwaistes Repository zurückzulassen, räume die Ressourcen wieder auf, indem du das folgende Kommando im `terraform`-Ordner ausführst:

```bash
terraform destroy
```

Bestätige die Löschung mit `yes`.

### Abschluss

In diesem Lab hast du gesehen, wie CI-Pipelines (Continuous Integration) genutzt werden können, um repetitive Aufgaben wie Formatierung und andere Prüfungen durchzuführen.
Neben GitHub Workflows gibt es noch andere Tools, um derartige CI-Pipelines aufzusetzen, wie **GitLab CI**, **Travis CI**, uvm.

## Lokale Umgebung bauen

### Lokale Umgebung mit Docker

#### 1. Klone das Repository

```bash
git clone <repository-url>
cd security-by-design/labs/00-github-workflows
```

#### 2. Baue den Container

```bash
docker build -t labs/00-github-workflows .
```

#### 3. Starten des Containers

```bash
docker run -it --name github-workflows --hostname github-workflows labs/00-github-workflows
```

#### Existierenden Container verwenden

Falls der Container bereits existiert:

```bash
docker start -i github-workflows
```

#### Container löschen/zurücksetzen

```bash
docker rm github-workflows
```
