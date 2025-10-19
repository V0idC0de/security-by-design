# ID Tokens

Diese Demo schafft die nötige Infrastruktur in einem Google Cloud Project, um das Lab `00-id-tokens` durchzuführen.

## Durchführung

> [!NOTE]
> Da dieses Lab als nötiges Backend zu [`labs/00-id-tokens`](/labs/00-id-tokens/)
> fungiert, sind die Anweisungen hier (noch™) nicht so detailliert.
> Es geht im Lab um ID-Tokens und nur zweitrangig um das nötige Setup auf GCP.

### 1. Vorbereitung und Login

```bash
cd terraform
terraform init
gcloud auth application-default login
```

### 2. Erstellung der Umgebung

```bash
terraform apply
```

Das `terraform apply` Kommando schlägt wegen der **Eventual Consistentcy** von GCPs Rechtezuweisungen eventuell fehl.
Falls der Fehler `Error 403: Permission 'iam.workloadIdentityPools.create' denied on resource ...` auftritt,
warte einen Moment und versuche es dann erneut - das Problem löst sich üblicherweise in wenigen Momenten/Minuten von selbst.

> [!NOTE]
> Der Terraform Output `project_number` ist für die Durchführung des Labs notwendig!
> Mit `terraform output` kann sie erneut angezeigt werden.

## Lokale Umgebung bauen

Dieses Lab kann mit Docker selbst nachvollzogen und durchgearbeitet werden.
Voraussetzung ist

1. eine Installation von `docker` ([Installation](https://docs.docker.com/engine/install/)).
2. ein Google Cloud Account

> [!NOTE]
> Statt `docker` kann auch der Lab-Ordner direkt genutzt werden. In diesem Fall müssen die folgenden Tools
> lokal installiert sein:
>
> 1. `terraform` ([Installation](https://developer.hashicorp.com/terraform/install))
> 2. `gcloud`/Google Cloud SDK ([Installation](https://cloud.google.com/sdk/docs/install))
> 3. Python
> 4. **Cloud Custodian**, Installation via Python-Pakete `c7n` und `c7n-gcp`

### Lokale Umgebung mit Docker

#### 1. Klone das Repository

```bash
git clone https://github.com/V0idC0de/security-by-design.git
```

#### 2. Baue den Container

> [!WARNING]
> Stelle sicher, dass du dich in diesem Verzeichnis `demos/00-gcp-wif` im Repository befindest,
> bevor du `docker build` ausführst! Für alle anderen `docker`-Befehle ist das Verzeichnis egal.

```bash
# Überspringe dieses Kommando, falls du schon in diesem Unterordner bist
cd security-by-design/demos/00-gcp-wif
```

```bash
# Für diese Demo werden mehrere Tools vorbereitet - der Build-Prozess kann wenige Minuten dauern.
docker build -t demos/00-gcp-wif .
```

#### 3. Starten des Containers

```bash
docker run -it --name demos-id-tokens --hostname demos-id-tokens demos/00-gcp-wif
```

> [!NOTE]
> `docker run` öffnet eine Shell innerhalb des Containers, die für das Lab genutzt werden kann.
> Wird das Terminal geschlossen, die Shell mit `CTRL + D`, `exit`, o.Ä. verlassen, stoppt der Container.
> Er wird allerdings nicht gelöscht und kann weiterverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden))

#### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container erneut zu betreten:

```bash
docker start -ai demos-id-tokens
```

#### Container löschen/zurücksetzen

Falls bereits ein Container mit diesem Namen existiert, kann er vorher entfernt werden.
Dies kann verwendet werden, um mit dem Lab neu zu starten.

```bash
docker rm -f demos-id-tokens
```

Nach Ausführung des zweiten Befehls befindet man sich direkt in einer Shell im Container und kann dort alle Übungen durchführen.
