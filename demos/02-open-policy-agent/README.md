# 02 Open Policy Agent & Terraform

- [02 Open Policy Agent \& Terraform](#02-open-policy-agent--terraform)
  - [Durchführung](#durchführung)
    - [1. GitHub Personal Access Token bereitstellen](#1-github-personal-access-token-bereitstellen)
    - [2. Terraform Plan ausführen](#2-terraform-plan-ausführen)
    - [3. Repository und Pull Request öffnen](#3-repository-und-pull-request-öffnen)
    - [4. GitHub Workflow beobachten](#4-github-workflow-beobachten)
    - [5. Analyse der Policy-Verletzungen](#5-analyse-der-policy-verletzungen)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [Lokale Umgebung mit Docker](#lokale-umgebung-mit-docker)
      - [1. Klone das Repository](#1-klone-das-repository)
      - [2. Baue den Container](#2-baue-den-container)
      - [3. Starten des Containers](#3-starten-des-containers)
      - [Existierenden Container verwenden](#existierenden-container-verwenden)
      - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In dieser Demo wird gezeigt, wie Terraform genutzt werden kann, um ein GitHub-Repository zu erstellen, das selbst Terraform-Konfigurationen und eine GitHub Actions Workflow-Datei enthält. Der Workflow analysiert geplante Terraform-Änderungen und prüft diese mit Hilfe von Open Policy Agent (OPA) und dem Tool `conftest` gegen definierte Richtlinien im `policy`-Verzeichnis.

Dadurch können Richtlinien automatisiert durchgesetzt werden, sodass bestimmte Konfigurationsänderungen – auch wenn sie technisch korrekt sind – aufgrund von Policy-Verstößen verhindert werden.

> [!NOTE]
> Diese Demo kann auch lokal durchgeführt werden. Hinweise dazu finden sich im Abschnitt [Lokale Umgebung bauen](#lokale-umgebung-bauen).

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich im Verzeichnis `02-open-policy-agent/workspace` befindest.

### 1. GitHub Personal Access Token bereitstellen

```bash
# Erstelle eine Kopie der Sample-Datei ohne .sample-Erweiterung
cp github-pat.auto.tfvars.json.sample github-pat.auto.tfvars.json

# Bearbeite die Datei, um deinen GitHub PAT einzufügen
nano github-pat.auto.tfvars.json
```

> [!NOTE]
> `.auto.tfvars` Dateien werden von Terraform bei jedem Lauf automatisch eingelesen.
> Das ist hier praktisch, da das GitHub-Token immer erforderlich ist.

> [!WARNING]
> Derartige Secrets sollten nicht in ein Repository committet werden.
> Daher schließt die `.gitignore` dieses Repositories alle `.tfvars` Dateien von Git aus,
> sodass keine versehentlichen Commits mit sensiblen Datein passieren.
> Einzige Ausnahme von der `.gitignore` sind die `sample.*.tfvars.json` Dateien, die später verwendet werden.

### 2. Terraform Plan ausführen

```bash
# Initialisiere das Repository einmalig
terraform init

# Führe Terraform Plan ohne Argumente aus
terraform plan
```

> [!WARNING]
> Das **Personal Access Token**, das Terraform in diesem Aufbauschritt zur Verfügung gestellt wird, wird in das erstellte Repository als Secret abgespeichert,
> um es dort bei einem `terraform plan` zu verwenden! Zwar lassen sich Secrets nicht von Personen mit Lesezugriff auslesen, doch wer Schreibzugriff in das Repository
> hat, kann Workflows nutzen, um das Token im Klartext zu erlangen. Das Repository wird mit `visibility = "private"` angelegt, sodass standardmäßig niemand Zugriff hat.
> Bedenke, dass jeder mit Schreibzugriff dein GitHub PAT auslesen kann. Zerstöre das GitHub Repository sicherheitshalber mit `terraform destroy`, sobald zu fertig bist.

> [!NOTE]
> Nach erfolgreichem Apply findest du im Terraform Output die URL zum neuen Repository sowie einen direkten Link zur Pull-Request-Erstellung.

### 3. Repository und Pull Request öffnen

Nutze den im Terraform Output angezeigten Link, um das neue Repository auf GitHub zu öffnen. Alternativ kannst du direkt zur Seite zum Erstellen eines Pull Requests springen.
Erstelle im Repository einen Pull Request, um z.B. den Branch `feature/add-settings` in den Hauptbranch (`main`) zu mergen.

> [!NOTE]
> Das Anlegen des Pull Requests löst automatisch den hinterlegten GitHub Actions Workflow aus.

### 4. GitHub Workflow beobachten

Klicke am unteren Ende des Pull Requests auf den aktiven **Workflow Run** und beobachte die Ausführung des Workflows.
Der Workflow führt einen `terraform plan` aus und prüft das Ergebnis mit **Open Policy Agents** `conftest` gegen die im Repository abgelegten Policies (siehe `/policy/*.rego`).

> [!WARNING]
> Der Workflow wird fehlschlagen, wenn geplante Änderungen gegen eine Policy verstoßen.

### 5. Analyse der Policy-Verletzungen

Klicke auf die Details des fehlgeschlagenen Workflow-Runs. Im Abschnitt, in dem `conftest` ausgeführt wurde, findest du genaue Hinweise, welche Policies verletzt wurden.
Am oberen Ende des **Workflow Runs** des Logs werden **Annotationen** angezeigt, die die Policy-Verstöße nochmal übersichtlich ganz oben auflisten.

> [!NOTE]
> Der Schritt `terraform plan` war erfolgreich, aber die Policy-Prüfung ist fehlgeschlagen.
> So werden unerwünschte Änderungen frühzeitig erkannt und blockiert, selbst wenn der `terraform plan` an an sich gültig ist.

### Abschluss

In dieser Demo wurde gezeigt, wie sich Terraform-Pläne mit Open Policy Agent und `conftest` automatisiert auf Policy-Konformität prüfen lassen. So können Teams sicherstellen, dass auch technisch korrekte, aber aus Compliance-Sicht unerwünschte Änderungen nicht versehentlich übernommen werden.

## Lokale Umgebung bauen

Diese Demo kann selbst nachvollzogen und durchgearbeitet werden.

Voraussetzung ist:

- eine Installation von `docker` (empfohlen), wobei du den Schritten für eine [Lokale Umgebung mit Docker](#lokale-umgebung-mit-docker) folgen kannst

ODER

- eine Installation von `terraform` ([Installation](https://developer.hashicorp.com/terraform/install))
- ein GitHub Account
- ein GitHub Personal Access Token (siehe Beschreibung der Variable in `variables.token.tf`)

### Lokale Umgebung mit Docker

#### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

#### 2. Baue den Container

> [!WARNING]
> Stelle sicher, dass du dich im Verzeichnis `demos/02-open-policy-agent` im Repository befindest, bevor du `docker build` ausführst!

```bash
cd security-by-design/demos/02-open-policy-agent
```

```bash
docker build -t demos/02-open-policy-agent .
```

#### 3. Starten des Containers

```bash
docker run -it --name open-policy-agent --hostname open-policy-agent demos/02-open-policy-agent
```

> [!NOTE]
> `docker run` öffnet eine Shell innerhalb des Containers, die für das Lab genutzt werden kann. Wird das Terminal geschlossen, bleibt der Container erhalten und kann wiederverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden)).

#### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container erneut zu betreten:

```bash
docker start -ai open-policy-agent
```

#### Container löschen/zurücksetzen

Falls bereits ein Container mit diesem Namen existiert, kann er vorher entfernt werden, um das Lab neu zu starten.

```bash
docker rm -f open-policy-agent
```

Nach Ausführung des zweiten Befehls befindet man sich direkt in einer Shell im Container und kann dort alle Übungen durchführen.
