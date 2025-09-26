# 05 Cloud Custodian

- [05 Cloud Custodian](#05-cloud-custodian)
  - [Durchführung (Teil 1 - On-Demand)](#durchführung-teil-1---on-demand)
    - [1. Ordnerstruktur und Vorbereitung](#1-ordnerstruktur-und-vorbereitung)
    - [2. Login mit Google Cloud SDK/CLI](#2-login-mit-google-cloud-sdkcli)
    - [3. Infrastruktur mit Terraform bereitstellen](#3-infrastruktur-mit-terraform-bereitstellen)
    - [4. Umgebung konfigurieren](#4-umgebung-konfigurieren)
    - [5. Wechsel in das Policies-Verzeichnis](#5-wechsel-in-das-policies-verzeichnis)
    - [6. Service Accounts prüfen](#6-service-accounts-prüfen)
    - [7. Policy anwenden und Ergebnisse prüfen](#7-policy-anwenden-und-ergebnisse-prüfen)
    - [8. Accounts wieder aktivieren](#8-accounts-wieder-aktivieren)
    - [9. Verbesserte Policy anwenden](#9-verbesserte-policy-anwenden)
    - [Zwischenstand](#zwischenstand)
  - [Durchführung (Teil 2 - Monitoring in Echtzeit)](#durchführung-teil-2---monitoring-in-echtzeit)
    - [1. Konfiguration der Echtzeit-Policy](#1-konfiguration-der-echtzeit-policy)
    - [2. Ersetzung des Platzhalters](#2-ersetzung-des-platzhalters)
    - [3. Deployment der Cloud Function](#3-deployment-der-cloud-function)
    - [4. Überprüfung der Überwachung](#4-überprüfung-der-überwachung)
    - [Zusammenfassung des Labs](#zusammenfassung-des-labs)
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

## Durchführung (Teil 1 - On-Demand)

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindet (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Ordnerstruktur und Vorbereitung

Untersuche den aktuellen Ordner und beachte die Unterordner 'terraform' und 'policies'.
Wechsle zur Vorbereitung in den `terraform` Ordner.

```bash
ls -l
cd terraform
```

> [!NOTE]
> (Optional) Betrachte die bereitgestellten Terraform-Dateien.
> Einige Tools wie `nano`, `vi`, `less`, `cat` oder `bat` stehen zur Verfügung.
> Alles im Ordner `terraform` dient dazu, Google Cloud Infrastruktur für die Demo bereitzustellen.

### 2. Login mit Google Cloud SDK/CLI

Führe die notwendigen Login-Kommandos für die Google Cloud CLI aus.

> [!NOTE]
> Die Warnung bei `gcloud auth application-default login` bezüglich des "Quota Project" werden
> gleich adressiert und können vorerst ignoriert werden.

```bash
gcloud auth login
gcloud auth application-default login
```

### 3. Infrastruktur mit Terraform bereitstellen

Erstelle die nötige Infrasturktur in Google Cloud. Es wird unter anderem ein Service Account erstellt,
dessen Name absichtlich gegen die Policy verstößt. Cloud Custodian wird diesen erkennen und das Problem behandeln.

```bash
terraform init
terraform apply
```

Die  `project_id` des erstellten Projekts in gleich wichtig. Details zu den Outputs findest du auch in der Datei `outputs.json`, die von Terraform erzeugt wird.

> [!NOTE]
> Terraform erstellt mehrere Ressourcen, die du dir im Plan ansehen kannst.
> Ein separates Projekt mit einem zufälligen Suffix wird für die Übung erstellt, worin alle Ressourcen enthalten sein werden.
> Zu bemerken sind die beiden Service Accounts, jeweils Policy-konform und -widrig, die wir gleich mit Cloud Custodian untersuchen.

### 4. Umgebung konfigurieren

Setze eine Hilfsvariable, um die `project_id` schneller verfügbar zu haben.

```bash
export PROJECT_ID="$(jq -r '.project_id' outputs.json)"
# Alternativ direkt aus Terraform (nur einer der beiden Befehle ist nötig)
export PROJECT_ID="$(terraform output -json | jq -r '.project_id.value')"
```

Setze Variablen und Konfigurationen, sodass für `gcloud` und andere Tools klar ist,
welches Googel Cloud Projekt standardmäßig genutzt werden soll.
So muss es später nicht ständig explizit genannt werden.

```bash
# Für alle `gcloud`-Aufrufe
gcloud config set project "$PROJECT_ID"
# Für andere Tools als `gcloud`, die auf Umgebungsvariablen achten
export CLOUDSDK_CORE_PROJECT="$PROJECT_ID"
# Verhindert Warnungen bzgl. Abrechnung - kosmetisch.
gcloud auth application-default set-quota-project "$PROJECT_ID"
```

### 5. Wechsel in das Policies-Verzeichnis

Wechsle zurück ins Home-Verzeichnis und dann in das `policies`-Verzeichnis, um mit Cloud Custodian fortzufahren.
Untersuche die Datei `sa-name-basic.policy.yaml` und beachte die Bedingungen, die Ressourcen identifizieren, welche gegen die Policy verstoßen.

```bash
cd
cd policies
bat sa-name-basic.policy.yaml
```

> [!INFO]
> Die Demo simuliert eine fiktive Richtlinie, die verlangt, alle Service Accounts mit `svc-` zu beginnen.
> Cloud Custodian beschreibt diese Bedingung via YAML in dieser recht intuitiv lesbaren Datei.
> Die Remediation-Aktion ist in der letzten Zeile: Service Accounts mit falschem Namen, werden deaktiviert.
> Löschung wäre ebenfalls möglich, hier jedoch weniger anschaulich.

### 6. Service Accounts prüfen

Liste alle Service Accounts auf und beachte, dass sie alle aktiviert sind:

```bash
gcloud iam service-accounts list
```

Die Accounts `svc-custodian-fn` und `barista-bot` wurden von Terraform erstellt. `...@appspot.gserviceaccount.com` ist ein von Google
automatisch erstellter, interner Account. Der `barista-bot` verstößt gegen die Richtlinie zu Namen und soll via Cloud Custodian behandelt werden.

### 7. Policy anwenden und Ergebnisse prüfen

Führe die Policy mit Cloud Custodian aus (ein `--output-dir` ist leider immer nötig) und gib die zu prüfende Policy an.
Anschließend liste erneut die Service Accounts und beachte, dass zwei Accounts deaktiviert wurden:

```bash
custodian run --output-dir logs sa-name-basic.policy.yaml
# Manchmal brauchen Änderungen an Service Accounts ein paar Momente, um korrekt angezeigt zu werden.
# Lasse ein paar Sekunden Zeit, bis du das `gcloud`-Kommando ausführst.
gcloud iam service-accounts list
```

Die Accounts `barista-bot` und der `App Engine default service account` (ein Standard-Account von Google Cloud) wurden von deaktiviert,
da sie gegen die Namenskonvention verstoßen. Der App Engine Standard-Account ist als Account mit unveränderlichem Namen aber gar nicht gemeint gewesen.

> [!WARNING]
> Hier ist eine wichtige Lektion schon erkennbar. Bei disruptiven Aktionen wie dem Deaktivieren oder Löschen von Accounts ist Vorsicht geboten.
> Unerwartete Nebeneffekte, wie das Deaktivieren von internen Google-Accounts, können auftreten.
> Es empfiehlt sich, bei Policies und Verstößen zunächst nur zu informieren, bevor tatsächlich gehandelt wird (Monitor-Mode oder "monitor-only").
> So werden Ausnahmen so praxisnah wie möglich erkannt und die endgültige Aktivierung führt zu weniger Störungen.

### 8. Accounts wieder aktivieren

Aktiviere die beiden Service Accounts wieder:

```bash
gcloud iam service-accounts enable "${PROJECT_ID}@appspot.gserviceaccount.com"
gcloud iam service-accounts enable "barista-bot@${PROJECT_ID}.iam.gserviceaccount.com"
# Manchmal brauchen Änderungen an Service Accounts ein paar Momente, um korrekt angezeigt zu werden.
# Lasse ein paar Sekunden Zeit, bis du das `gcloud`-Kommando ausführst.
gcloud iam service-accounts list
```

### 9. Verbesserte Policy anwenden

Untersuche die Datei `sa-name-improved.policy.yaml`, die eine zusätzliche Prüfung enthält.
Manuell angelegte Service Accounts enden in Google Cloud immer auf `iam.gserviceaccount.com`.
Diese zusätzliche Bedingung verhindert ungewollten "Beifang".

Führe die verbesserte Policy aus:

```bash
bat sa-name-improved.policy.yaml
custodian run --output-dir logs sa-name-improved.policy.yaml
```

Prüfe erneut die Service Accounts:

```bash
gcloud iam service-accounts list
```

Nun wurde nur der beabsichtigte Account (`barista-bot`) deaktiviert.

> [!NOTE]
> So werden Prüfungen der Policies "On-Demand" umgesetzt. Zwar ist dieses Verfahren effektiv und eigenet sich zur regelmäßigen Überprüfung,
> allerdings hindert es Nutzer grundsätzlich nicht daran, policy-widrige Namen für Service Accounts zu vergeben und bis zur nächsten Prüfung zu nutzen!

### Zwischenstand

Cloud Custodian erkennt und behebt Policy-Verstöße zuverlässig und automatisiert – auch in großen Cloud-Umgebungen wie Google Cloud.
Die Remediation erfolgt „On-Demand“ bei Ausführung, praktisch etwa für Audits oder CI/CD-Pipelines.

Allerdings können zwischen den Prüfungen weiterhin policy-widrige Ressourcen deployed und genutzt werden.
Eine Echtzeit-Durchsetzung fehlt bislang. Im nächsten Abschnitt wird gezeigt, wie dies mit einem event-basierten System möglich ist.

## Durchführung (Teil 2 - Monitoring in Echtzeit)

> Die folgenden Schritte nehmen an, dass du dich im Ordner `policies` dieser Demo befindest.
> Sollte das nicht so sein, nutze `cd ~/policies`, um dort hinzugelangen (`pwd` zeigt auch das aktuelle Verzeichnis an).

Im zweiten Teil dieser Demo wird Cloud Custodian genutzt, um Richtlinien nicht nur bei manueller Ausführung, sondern auch automatisch in Echtzeit umzusetzen.
Dafür muss die Policy um die Modus-Einstellung `type: gcp-audit` erweitert werden.

So wird eine Google Cloud Function, sowie die erforderlichen Logging-Einstellungen konfiguriert, sodass die Funktion automatisch ausgelöst wird.
Dies geschieht dann, sobald ein Ereignis im Log erkannt wird, das einen Service Account erstellt oder explizit aktiviert – also potenziell gegen die Policy verstößt.
Cloud Custodian wird dann sofort ausgeführt und die Remediation erfolgt unmittelbar und ohne manuelles Eingreifen.

> [!NOTE]
> Da Cloud Functions parallel ausgeführt werden können und hochgradig skalierbar sind, können quasi beliebig viele Verstöße gleichzeitig geprüft und behoben werden.
> Cloud Custodian übernimmt die komplette Bereitstellung von Source Code und der Funktion selbst, sodass der Nutzer lediglich die Policy schreibt.
> Dieser Ansatz skaliert deutlich besser, als regelmäßige explizite Ausführung, z.B. via `crond`.

### 1. Konfiguration der Echtzeit-Policy

Untersuche die neue Policy-Datei `sa-name-realtime.template.yaml`. Achte speziell auf das Feld `service-account` und den Platzhalter `PROJECT_ID`.

```bash
bat sa-name-realtime.template.yaml
```

Die folgenden Details sind hier wichtig:

- Der Modus `gcp-audit` ist gesetzt, wodurch die Policy als Echtzeit-Überwachung deployed und nicht als einmalige Prüfung ausgeführt wird.
- Ein expliziter Service Account ist angegeben, in dessen Namen die Cloud Function ausführt wird
  - Dieser Service Account benötigt die Berechtigung, die Remediation-Aktion durchzuführen
  - `roles/iam.serviceAccountAdmin` wurde bereits via Terraform an diesen Service Account vergeben

### 2. Ersetzung des Platzhalters

Da der Name des Service Accounts von der Projekt-ID abhängt, kann er im Voraus nicht ermittelt werden.
Trage deine Projekt-ID manuell ein oder nutze das folgende Kommando, um das automatisch zu tun.

> Falls du die Änderung manuell machst, muss die Datei zu `sa-name-realtime.policy.yaml` umbenannt/kopiert werden.
> Die nachfolgenden Schritte nach diesem gehen davon aus, dass die Datei so heißt.

```bash
sed "s/PROJECT_ID/${PROJECT_ID}/" sa-name-realtime.template.yaml | tee sa-name-realtime.policy.yaml
```

### 3. Deployment der Cloud Function

```bash
custodian run --output-dir logs sa-name-realtime.policy.yaml
```

> [!WARNING]
> Sollte hier eine Fehlermeldung mit `"Permission denied on 'locations/...` erscheinen, ist es möglich,
> dass die Region keine Cloud Functions der 1. Generation unterstützt. Die Region kann auch weggelassen werden.

Das Deployment von Cloud Functions dauert einen Moment, wegen den Build-Prozesses im Hintergrund.
Prüfe mit dem folgenden Kommendo, ob der `STATE` auf `ACTIVE` steht, dann fahre fort.

```bash
gcloud functions list
```

### 4. Überprüfung der Überwachung

Stelle sicher, dass der Service Account `barista-bot` aktuell deaktiviert ist.

```bash
gcloud iam service-accounts disable "barista-bot@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud iam service-accounts list
```

Teste die Echtzeit-Überwachung, indem der `barista-bot` Service Account aktiviert wird.
Im direkten Anschluss nutzen wir `watch`, um wiederholt die Service Accounts zu listen.
So können wir die Deaktivierung beobachten.

```bash
# Beide Zeilen können auf einmal kopiert, eingefügt und ausgewführt werden.
gcloud iam service-accounts enable "barista-bot@${PROJECT_ID}.iam.gserviceaccount.com" && \
watch -n 3 gcloud iam service-accounts list
```

Beobachte, wie sich der Status des Service Accounts zu `DISABLED: false` und wieder `DISABLED: true` verändert.
Ergebnis: `barista-bot` Account bleibt weiterhin deaktiviert – Cloud Custodian macht die Aktivierung sofort rückgängig.

### Zusammenfassung des Labs

Das Lab demonstriert, wie Tools wie Cloud Custodian Richtlinien und Vorgaben als Code umsetzen.
Im Gegensatz zu Freitext-Richtlinien, die auf menschlicher Interpretation beruhen, kann Policy-as-Code
**automatisiert, wiederholbar und skalierbar** durch Maschinen umgesetzt werden.
Cloud Custodian kann sowohl On-Demand in CI/CD-Pipelines integriert werden (Shift-Left Security),
als auch im Betrieb durch ereignisbasierte Überwachung und automatische Remediation.

Auch andere Aktionen, wie das Löschung, Benachrichtigungen per E-Mail oder Chat, oder Integrationen mit anderen Tools sind möglich.

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
> Stelle sicher, dass du dich in diesem Verzeichnis `labs/05-cloud-custodian` im Repository befindest,
> bevor du `docker build` ausführst! Für alle anderen `docker`-Befehle ist das Verzeichnis egal.

```bash
# Überspringe dieses Kommando, falls du schon in diesem Unterordner bist
cd security-by-design/labs/05-cloud-custodian
```

```bash
# Für diese Demo werden mehrere Tools vorbereitet - der Build-Prozess kann wenige Minuten dauern.
docker build -t labs/05-cloud-custodian .
```

#### 3. Starten des Containers

```bash
docker run -it --name cloud-custodian --hostname cloud-custodian labs/05-cloud-custodian
```

> [!NOTE]
> `docker run` öffnet eine Shell innerhalb des Containers, die für das Lab genutzt werden kann.
> Wird das Terminal geschlossen, die Shell mit `CTRL + D`, `exit`, o.Ä. verlassen, stoppt der Container.
> Er wird allerdings nicht gelöscht und kann weiterverwendet werden (siehe [Existierenden Container verwenden](#existierenden-container-verwenden))

#### Existierenden Container verwenden

Um einen bestehenden, gestoppten Container erneut zu betreten:

```bash
docker start -ai cloud-custodian
```

#### Container löschen/zurücksetzen

Falls bereits ein Container mit diesem Namen existiert, kann er vorher entfernt werden.
Dies kann verwendet werden, um mit dem Lab neu zu starten.

```bash
docker rm -f cloud-custodian
```

Nach Ausführung des zweiten Befehls befindet man sich direkt in einer Shell im Container und kann dort alle Übungen durchführen.
