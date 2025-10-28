# 05 Open Policy Agent & Terraform

- [05 Open Policy Agent \& Terraform](#05-open-policy-agent--terraform)
  - [Durchführung](#durchführung)
    - [1. Betrachte das Setup im Container](#1-betrachte-das-setup-im-container)
    - [2. GitHub Login](#2-github-login)
    - [3. Terraform Plan ausführen](#3-terraform-plan-ausführen)
    - [4. Repository und Pull Request öffnen](#4-repository-und-pull-request-öffnen)
    - [5. GitHub Workflow beobachten](#5-github-workflow-beobachten)
    - [6. Analyse der Policy-Verletzungen](#6-analyse-der-policy-verletzungen)
    - [7. Prüfung der Policy-Dateien](#7-prüfung-der-policy-dateien)
    - [8. Policy-Verletzungen beheben](#8-policy-verletzungen-beheben)
      - [8.1 Fix via `git`](#81-fix-via-git)
      - [8.2 Fix via GitHub-Website](#82-fix-via-github-website)
    - [9. Erneute Workflow-Ausführung prüfen](#9-erneute-workflow-ausführung-prüfen)
    - [10. Aufräumen](#10-aufräumen)
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
> Wenn keine Lab-Umgebung zur Verfügung gestellt wird, kann das Lab mit Docker auch lokal ausprobiert werden.
> Eine Nutzungsanleitung zum lokalen Aufsetzen des Labs findet sich unter [Lokale Umgebung bauen](#lokale-umgebung-bauen).

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindet (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Betrachte das Setup im Container

```bash
# Dateien auflisten
tree

# Wechsel ins Verzeichnis mit dem Terraform Code
cd terraform
```

### 2. GitHub Login

Folge den Schritten in [GitHub Login](/github-login.md).

> [!NOTE]
> Wenn du diesen Prozess bereits kennst, kannst du einfach `gh auth login -s delete_repo` ausführen.
> Die verlinkte Seite erklärt die Schritte dieses Kommandos lediglich genauer.

Anschließend führe den folgenden Befehl aus, um das GitHub Token als Variable für Terraform
zur Verfügung zu stellen (siehe auch `variables.token.tf`), indem es als Umgebungsvariable
`TF_VAR_` gefolgt vom Namen der Terraform-Variablen gesetzt wird.

```bash
export TF_VAR_github_token="$(gh auth token)"
```

> [!WARNING]
> Das **Personal Access Token**, das Terraform in diesem Aufbauschritt zur Verfügung gestellt wird,
> wird im erstellten Repository als [GitHub Secret](https://docs.github.com/en/actions/concepts/security/secrets)
> gespeichert, um es später für die GitHub Workflows zu nutzen.
> Zwar lassen sich Secrets nicht von Personen mit Lesezugriff auslesen, doch wer Schreibzugriff auf
> das Repository hat, kann Workflows nutzen, um das Token im Klartext zu erlangen.
>
> Das Repository wird mit `visibility = "public"` angelegt, doch das Token wird dadurch **nicht** öffentlich sichtbar.
> Zerstöre das GitHub Repository dennoch sicherheitshalber mit `terraform destroy`, sobald du fertig bist (siehe [Schritt 10](#10-aufräumen)).

### 3. Terraform Plan ausführen

Terraform wird in diesem Schritt nur genutzt, um die nötige Infrastruktur in GitHub aufzubauen.
Es nicht nicht nötig, alle Ressourcen in diesem Schritt nachzuvollziehen - du kannst es natürlich trotzdem tun.

```bash
# Initialisiere das Repository einmalig
terraform init

# Wende den Plan an, um das Repository zu erstellen.
# Die Warnung "Deprecated attribute" kann ignoriert werden - sie stört uns nicht beim Lab.
terraform apply
```

Nach erfolgreichem `terraform apply` findest du im Terraform Output die URL zum neuen Repository sowie einen direkten Link zur Pull-Request-Erstellung. Mit `terraform output` kommst du schnell an die Outputs.

### 4. Repository und Pull Request öffnen

Nutze den im Terraform Output angezeigten Link, um das neue Repository auf GitHub zu öffnen.
Wähle oben den Tab **"Pull Requests** und erstelle im Repository dann einen Pull Request,
um den Branch `feature/add-repositories` in den Hauptbranch (`main`/`master`) zu mergen.

> [!NOTE]
> Das Anlegen des Pull Requests löst automatisch den hinterlegten GitHub Actions Workflow aus.
> Dieses Auslösen dauert bei GitHub manchmal 5-10 Sekunden, bis es im Pull Request angezeigt wird.

### 5. GitHub Workflow beobachten

Scrolle zum unteren Ende des Pull Requests und beobachte die Ausführung des **Workflow Run**s `Terraform Plan`.
Der Workflow führt einen `terraform plan` aus und prüft das Ergebnis mit dem Tool `conftest` gegen
die im Repository abgelegten Policies (siehe `/policy/*.rego`).

> [!WARNING]
> Der Workflow wird fehlschlagen, da wir Änderungen haben, die gegen eine Policy verstoßen.
> Merke hierbei auch, dass der Button **Merge pull request** deaktiviert ist, da dieser Workflow
> erfolgreich sein **muss**, bevor gemerged werden darf! Dies ist von einer **Branch Protection** festgelegt worden.

Hinweis: `conftest` ist eine kompaktere von des Haupt-Tools **Open Policy Agent**.

### 6. Analyse der Policy-Verletzungen

Klicke auf den fehlgeschlagenen Workflow am unteren Ende des Pull Requests, um die Details der Ausführung zu sehen.

Am oberen Ende des **Workflow Runs** des Logs werden **Annotationen** angezeigt, die die Policy-Verstöße übersichtlich auflisten.
Falls du die Workflow-Seite bereits geöffnet hattest, musst du sie ggf. aktualisieren, da sie vom späten Schritt `Run OPA Policy Check` geschrieben werden.

> [!NOTE]
> Der Schritt `terraform plan` war erfolgreich, aber die Policy-Prüfung ist fehlgeschlagen.
> So werden unerwünschte Änderungen frühzeitig erkannt und blockiert, selbst wenn der `terraform plan` an an sich gültig ist.

### 7. Prüfung der Policy-Dateien

Sieh dir nun auf der GitHub-Website deines Repositories die Dateien im Ordner `/policy` genauer an.
Vollziehe die Absicht der Policy anhand ihres Codes nach.

Die Dateien nutzen den sogenannten **Rego-Syntax** und fungieren als Filter für einen Input.
Dieser Input ist in diesem Fall eine Auflistung der geplanten Änderungen von **Terraform** im JSON-Format.
Wenn der Filter im Input ein Ergebnis findet, wurde ein Policy-Verstoß erkannt.

Es ist nicht erforderlich, den **Rego-Syntax** im Detail zu kennen, um die Grundzüge hier nachzuvollziehen.
Es genügt völlig, wenn du die Stellen erkennst, an denen die entscheidenden Vergleiche gemacht werden.

> [!NOTE]
> (Optional) In der Datei `.github/workflows/ci.yml` kann in Zeile 39-40 und Zeile 48 nachvollzogen werden,
> wie `conftest` aufgerufen wird und wie man einen `terraform plan` im JSON-Format erhält.
> Dies kann auch für andere Automatisierungen praktisch sein, z.B. um Change-Tickets zu erstellen,
> wenn bestimmte Ressourcen(-Typen) verändert werden oder destruktive Aktionen geplant sind.

### 8. Policy-Verletzungen beheben

Kehre zurück in die Laborumgebung und behebe die Policy-Verstöße.
Dies kann mit `git` in der Konsole erledigt werden oder auf der GitHub-Website.
Wähle **einen** der beiden Wege, die im Folgenden beschrieben sind.

#### 8.1 Fix via `git`

Kehre in die Laborumgebung zurück und wechsle mit `cd` (ohne Parameter) ins Home-Verzeichnis.
Klone dann das GitHub-Repository, das eben erstellt wurde.

```bash
cd
gh repo clone demo-open-policy-agent
cd demo-open-policy-agent
```

Wechsele auf den Branch, auf den sich der Pull Request bezieht.

```bash
git checkout add-repositories
```

Behebe den Policy-Verstoß in `main.tf`, indem du die **Visibility** von `public` auf `private` setzt.
Neben `nano` kann natürlich auch jeder andere Editor genutzt werden.

```bash
nano main.tf
# Drücke zum Speichern und Verlassen "STRG + S", dann "STRG + X"
```

Um den Repository-Namen zu beheben, sehen wir in die `settings.yaml` Datei.
Behebe dort das verbotene Wort `coffee` im Repository-Namen und ersetze es durch etwas anderes.
Nutze für den ersatz nur Buchstaben, Zahlen und Bindestriche.
Da dies der Repository-Name wird, sollten keine dafür ungültigen Zeichen enthalten sein.

```bash
nano settings.yaml
# Drücke zum Speichern und Verlassen "STRG + S", dann "STRG + X"
```

Mit `git status` sehen wir die beiden geänderten Dateien, committen diese jetzt und pushen danach in GitHub-Repository.

```bash
git add main.tf settings.yaml
git commit -m "fix: Policy"
git push
```

#### 8.2 Fix via GitHub-Website

// TODO

### 9. Erneute Workflow-Ausführung prüfen

Kehre zum Pull Request zurück, wo der GitHub Workflow durch den Push der Änderungen erneut ausgeführt werden sollte.
Eventuell muss die Website des Pull Requests aktualisiert werden, um die erneute Ausführung anzuzeigen.

Diesmal sollte der Workflow erfolgreich durchlaufen, wenn alle Fehler korrekt behoben wurden.
Merke, wie der Button **Merge pull request** nun aktiv wird, nachdem der Workflow erfolgreich beendet wurde.

Merge den Pull Request zum Abschluss - der Workflow wird die Änderungen nicht wirklich anwenden, da er keinen `terraform apply` enthält.

### 10. Aufräumen

Um kein verwaistes Repository zurückzulassen, räume die Ressourcen wieder auf, indem du das folgende Kommando im `terraform`-Ordner ausführst:

```bash
terraform destroy
```

### Abschluss

In dieser Demo wurde gezeigt, wie sich Terraform-Pläne mit Open Policy Agent und `conftest` automatisiert auf Policy-Konformität prüfen lassen.
So können Teams sicherstellen, dass auch technisch korrekte, aber aus Compliance-Sicht unerwünschte Änderungen nicht versehentlich übernommen werden.

## Lokale Umgebung bauen

Dieses Lab kann mit Docker selbst nachvollzogen und durchgearbeitet werden.
Voraussetzung ist

1. eine Installation von `docker` ([Installation](https://docs.docker.com/engine/install/)).
   1. Alternativ kann auch der Lab-Ordner direkt genutzt werden, wobei `terraform` ([Installation](https://developer.hashicorp.com/terraform/install)) installiert sein muss
2. ein GitHub Account
3. ein GitHub Personal Access Token (siehe [GitHub PAT](/GitHub-PAT.md))

### Lokale Umgebung mit Docker

#### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

#### 2. Baue den Container

> [!WARNING]
> Stelle sicher, dass du dich im Verzeichnis `labs/05-open-policy-agent` im Repository befindest, bevor du `docker build` ausführst!

```bash
cd security-by-design/labs/05-open-policy-agent
```

```bash
docker build -t labs/05-open-policy-agent .
```

#### 3. Starten des Containers

```bash
docker run -it --name open-policy-agent --hostname open-policy-agent labs/05-open-policy-agent
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
