# 01 Terraform

- [01 Terraform](#01-terraform)
  - [Durchführung](#durchführung)
    - [1. GitHub Personal Access Token bereitstellen](#1-github-personal-access-token-bereitstellen)
    - [2. Terraform Plan ausführen](#2-terraform-plan-ausführen)
    - [3. Terraform mit Variablen-Datei ausführen](#3-terraform-mit-variablen-datei-ausführen)
    - [4. Repositories auf GitHub überprüfen](#4-repositories-auf-github-überprüfen)
    - [5. Weitere Dateien hinzufügen](#5-weitere-dateien-hinzufügen)
    - [7. Manuelle Änderungen und State Drift demonstrieren](#7-manuelle-änderungen-und-state-drift-demonstrieren)
    - [8. Idempotenz demonstrieren](#8-idempotenz-demonstrieren)
    - [9. Infrastruktur abbauen](#9-infrastruktur-abbauen)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [Lokale Umgebung mit Docker](#lokale-umgebung-mit-docker)
      - [1. Klone das Repository](#1-klone-das-repository)
      - [2. Baue den Container](#2-baue-den-container)
      - [3. Starten des Containers](#3-starten-des-containers)
      - [Existierenden Container verwenden](#existierenden-container-verwenden)
      - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In dieser Demo wird gezeigt, wie Terraform zur Verwaltung von GitHub-Repositories eingesetzt werden kann. Mit Terraform können wir Ressourcen wie **Repositories**, **Einstellungen** und **Dateien** innerhalb dieser Repositories basierend auf **Input-Variablen** erstellen und verwalten.

Wir werden schrittweise die Terraform-Konfiguration erweitern, um zu zeigen, wie Terraform auf Änderungen reagiert, diese plant und umsetzt. Außerdem werden wir demonstrieren, was passiert, wenn manuelle Änderungen außerhalb von Terraform vorgenommen werden (**"State Drift"**) und wie Terraform darauf reagiert.

> [!NOTE]
> Wenn keine Demo-Umgebung zur Verfügung gestellt wird, kann das Lab mit Terraform auch lokal ausprobiert werden.
> Eine Nutzungsanleitung zum lokalen Aufsetzen des Labs findet sich unter [Lokale Umgebung bauen](#lokale-umgebung-bauen).

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich im Verzeichnis `01-terraform/workspace` befindest.

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

### 2. Terraform Plan ausführen

```bash
# Initialisiere das Repository einmalig
terraform init

# Führe Terraform Plan ohne Argumente aus
terraform plan
```

> [!NOTE]
> Beachte, wie Terraform nach fehlenden Eingabevariablen fragt.
> Bei interaktiver Nutzung ist das praktisch, doch in einer automatisierten Umgebung
> wie einer GitHub-Pipeline wäre dies problematisch.
> 
> Breche diesen Befehl mit CTRL+C ab.

```bash
# Führe Terraform Plan mit dem Argument aus, das interaktive Eingaben verhindert
terraform plan -input=false
```

> [!NOTE]
> Beachte, wie Terraform sofort fehlschlägt, ohne nach Variablen zu fragen.
> So würde Terraform in einer automatisierten Umgebung typischerweise ausgeführt werden.

### 3. Terraform mit Variablen-Datei ausführen

```bash
# Betrachte die Input-Variablen
less variables.tf

# Betrachte den Input des ersten Inputs
less inputs/sample.1.tfvars.json
 
# (Optional) Finde mit einer kurzen Suche die Orte,
# an denen die Variablen mit `var.VARNAME` verwendet werden.
# Vollziehe diese Verwendung nach.
grep -F -C 5 'var.' *.tf

# Führe Terraform Plan mit einer Variablen-Datei aus
terraform plan -var-file inputs/sample.1.tfvars.json
```

> [!NOTE]
> Beachte die Namen für jede Ressource und welche Werte aus den Variablen stammen.
> Die Ressourcen bei denen `for_each` genutzt wird, werden als Map angelegt, deren `key`s
> auf dem Wert von `for_each` basieren.

```bash
# Wende die Konfiguration an.
# Eine Bestätiung mit "yes" ist notwendig.
# `-auto-approve` überspringt diese und bestätigt automatisch.
terraform apply -var-file inputs/sample.1.tfvars.json
```

### 4. Repositories auf GitHub überprüfen

Besuche GitHub und überprüfe, dass die Repositories korrekt erstellt wurden.

`terraform output` zeigt die Outputs der aktuellen Terraform-Konfiguration,
wo die URLs der Repositories schnell einsehbar sind.

### 5. Weitere Dateien hinzufügen

> [!NOTE]
> Dieselbe Input-Datei `sample.1.tfvars.json` könnte auch verändert und wiederverwendet werden.
> Dass hier verschiedene Input-Dateien genutzt werden dient nur der besseren Durchführbarkeit 
> ohne manuelle Änderungen an den Dateien.

```bash
# Betrachte die Unterschiede zwischen den Input-Dateien
diff inputs/sample.1.tfvars.json inputs/sample.2.tfvars.json

terraform apply -var-file inputs/sample.2.tfvars.json

> [!NOTE]
> Beachte, dass keine bestehenden Ressourcen geändert werden, da Terraform keinen Grund dafür sieht.
> Nur die Dateien, die hinzugefügt werden sollen, sind im Plan gelistet.
> Terraform ermittelt diese Unterschiede selbstständig.

### 6. Default Branch ändern

```bash
terraform plan -var-file inputs/sample.3.tfvars.json
```

> [!NOTE]
> Beachte, dass der Plan mehrere Änderungen an verschiedenen Ressourcen enthält, obwohl wir nur eine Eingabevariable geändert haben. Dies zeigt, wie Terraform korrekt alle Variablen und Querverweise innerhalb der Konfiguration neu bewertet und erkennt, welche Attribute sich aufgrund einer Eingabeänderung ändern.

> [!NOTE]
> Einige Ressourcen, wie der Default-Branch-Name, der von `main` zu `production` wechselt, 
> sind sogenannte "in-place updates". Dabei wird die bestehende Ressource verändert, ohne sie neu zu erstellen.

> [!WARNING]
> Die Dateien, die im Repository erstellt werden, ändern den Branch, auf dem sie angelegt sind.
> Auf GitHub lassen sich Dateiobjekte allerdings nicht mehr verschieden - sie sind **Immutable**.
> Terraform kommentiert das mit **"forces replacement"** und zeigt damit an, dass diese Dateiobjekte zerstört
> und neu erstellt werden müssen, um den Zielzustand zu erreichen.
> Eine Ressource, die zerstört und neu erstellt wird, ist eine potenziell destruktive Aktion und sollte mit Vorsicht durchgeführt werden.

```bash
terraform apply -var-file inputs/sample.3.tfvars.json
```

Besuche GitHub und überprüfe, dass die Default-Branch-Namen geändert wurden.

### 7. Manuelle Änderungen und State Drift demonstrieren

1. Gehe zu einem der Repositories auf GitHub (nutze `terraform output` um schnell die URLs zu sehen)
2. Bearbeite eine von Terraform verwaltete Datei (`SECURITY.md` oder `LICENSE.md`), z.B. über den GitHub-Editor
3. Ändere den Inhalt und committe die Änderung direkt auf den `production` Branch

Führe jetzt Terraform erneut aus:

```bash
terraform apply -var-file inputs/sample.3.tfvars.json
```

> [!NOTE]
> Beachte, wie Terraform erkennt, dass eine der Dateien nicht mehr den erwarteten Inhalt hat. 
> Diese Änderung außerhalb von Terraform wird als **"State Drift"** bezeichnet und ist generell unerwünscht,
> da Infrastructure-as-Code darauf abzielt, dass alles genau so existiert, wie im Code konfiguriert.
> Terraform wird die Änderung erkennen und den gewünschten Zustand wiederherstellen wollen.

Überprüfe nach der Ausführung von Terraform, dass die Datei wieder den ursprünglichen Inhalt hat.

### 8. Idempotenz demonstrieren

```bash
terraform apply -var-file inputs/sample.3.tfvars.json
```

> [!NOTE]
> Beachte, dass Terraform einen Plan ohne Änderungen liefert, da alles wie in der Konfiguration beschrieben existiert. > Dies zeigt die Idempotenz von Terraform - wiederholte Ausführungen führen zum gleichen Ergebnis,
> statt Ressourcen doppelt zu erstellen, o.Ä.

### 9. Infrastruktur abbauen

Zum Abbau dieser Testumgebung, führe das folgende `terraform destroy` Kommando aus.
Es bildet das Gegenstück zu `terraform apply`.

```bash
terraform destroy -var-file inputs/sample.3.tfvars.json
```

### Abschluss

Die Demonstration zeigte, wie Terraform Input-Variablen und Konfigurtionen in echte Infrastruktur verwandet.
Ebenso wird auf Änderungen der Infrastruktur oder gewünschen Konfiguration reagiert.

Beachte im letzten Schritt beim Abbau besonders, wie Terraform zuverlässig und vollständig alle verwalteten Ressourcen
zerstört. Übertrage dies auf ein praktisches Szenario, in dem z.B. Infrastruktur für eine Webapplikation erstellt wird und verschiedene Ressourcen wie Storage Buckets, Domainnamen, Domain-Einträge, IP-Adressen, Firewall-Regeln und ähnliche Ressourcen angelegt werden.

Ohne ein Tool wie Terraform ist es schwierig, diese Ressourcen korrekt einzeln abzubauen und 
logische Verbindungen zwischen Werten in der Konfiguration akkurat abzubilden.
Manuell gepflegte Listen veralten schnell führen schnell dazu, dass einige dieser Ressourcen in einem schwer
zu wartenden "Shadow-IT"-Dasein verschwinden.
Terraform schließt diese Lücke durch eine zentrale und überprüfbare Verwaltung der Ressourcen und kann zuverlässig Änderungen an mehreren Ressourcen vornehmen bzw. sie zerstören, wenn die gewünschte Konfiguration dies erfordert.

## Lokale Umgebung bauen

Diese Demo kann selbst nachvollzogen und durchgearbeitet werden.

Voraussetzung ist:

- eine Installation von `terraform` ([Installation](https://developer.hashicorp.com/terraform/install)) (siehe Anmerkung unten)
- ein GitHub Account
- ein GitHub Personal Access Token (siehe Beschreibung der Variable in `variables.token.tf`)

> [!NOTE]
> Alternativ kann eine lokale Installation von `terraform` durch `docker` ersetzt werden.
> Befolge dafür die Schritte [Lokale Umgebung mit Docker](#lokale-umgebung-mit-docker).

### Lokale Umgebung mit Docker

#### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

#### 2. Baue den Container

> [!WARNING]
> Stelle sicher, dass du dich in diesem Verzeichnis `demos/01-terraform` im Repository befindest,
> bevor du `docker build` ausführst! Für alle anderen `docker`-Befehle ist das Verzeichnis egal.

```bash
# Überspringe dieses Kommando, falls du schon in diesem Unterordner bist
cd security-by-design/demos/01-terraform
```

```bash
docker build -t demo/terraform .
```

#### 3. Starten des Containers

```bash
docker run -it --name terraform --hostname terraform demo/terraform
```

> [!NOTE]
> `docker run` öffnet eine Shell innerhalb des Containers, die für das Lab genutzt werden kann.
> Wird das Terminal geschlossen, die Shell mit `CTRL + D`, `exit`, o.Ä. verlassen, stoppt der Container.
> Er wird allerdings nicht gelöscht und kann weiterverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden))

#### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container erneut zu betreten:

```bash
docker start -ai terraform
```

#### Container löschen/zurücksetzen

Falls bereits ein Container mit diesem Namen existiert, kann er vorher entfernt werden.
Dies kann verwendet werden, um mit dem Lab neu zu starten.

```bash
docker rm -f terraform
```

Nach Ausführung des zweiten Befehls befindet man sich direkt in einer Shell im Container und kann dort alle Übungen durchführen.
