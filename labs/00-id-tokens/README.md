# 00 ID Tokens

- [00 ID Tokens](#00-id-tokens)
  - [Durchführung](#durchführung)
    - [1. Ordnerstruktur und Vorbereitung](#1-ordnerstruktur-und-vorbereitung)
    - [2. GitHub Login](#2-github-login)
    - [3. Repository erstellen](#3-repository-erstellen)
    - [4. Repository im Browser öffnen](#4-repository-im-browser-öffnen)
    - [5. ID Token Workflow ausführen](#5-id-token-workflow-ausführen)
    - [6. Workflow verfolgen](#6-workflow-verfolgen)
    - [7. Ergebnisse betrachten](#7-ergebnisse-betrachten)
    - [8. ID-Token decodieren](#8-id-token-decodieren)
    - [9. ID-Token untersuchen](#9-id-token-untersuchen)
    - [10. Aufräumen](#10-aufräumen)
    - [Abschluss](#abschluss)
  - [Lokale Umgebung bauen](#lokale-umgebung-bauen)
    - [1. Klone das Repository](#1-klone-das-repository)
    - [2. Baue den Container](#2-baue-den-container)
    - [3. Starten des Containers](#3-starten-des-containers)
    - [Existierenden Container verwenden](#existierenden-container-verwenden)
    - [Container löschen/zurücksetzen](#container-löschenzurücksetzen)

In diesem Lab wird die Nutzung eines **ID-Tokens** demonstriert, das zur Anmeldung bei Google Cloud genutzt wird.
Dabei wird auf die Nutzung statische Zugangsdaten (z.B. einen API Key, Passwörter, o.Ä.) vollständig verzichtet.

> [!NOTE]
> Wenn keine Lab-Umgebung zur Verfügung gestellt wird, kann das Lab mit Terraform auch lokal ausprobiert werden.
> Eine Nutzungsanleitung zum lokalen Aufsetzen des Labs findet sich unter [Lokale Umgebung bauen](#lokale-umgebung-bauen).

Bei lokaler Ausführung des Labs außerhalb einer bereitgestellten Testumgebung muss folgendes beachtet werden.

> [!WARNING]
> Dieses Lab erfordert, dass in Google Cloud ein entsprechendes Projekt konfiguriert ist!
> Eine bereitgestellte Lab-Umgebung sollte das bereits haben. Falls das Lab lokal ausgeführt wird,
> ist es möglich, dass du dies selbst aufsetzen musst und dafür einen Google Cloud Account benötigst.
> Die Nutzung von Google Cloud kann Kosten verursachen.

## Durchführung

Die folgenden Schritte gehen davon aus, dass du dich in der Laborumgebung befindest (bereitgestellte Umgebung oder lokal ausgeführter Container).

### 1. Ordnerstruktur und Vorbereitung

Untersuche den aktuellen Ordner und wechsle in das Verzeichnis `lab-id-tokens`.

```bash
ls -l
cd lab-id-tokens
```

### 2. GitHub Login

Folge den Schritten in [GitHub Login](/github-login.md).

### 3. Repository erstellen

Erstelle ein neues privates Repository unter deinem eigenen GitHub-Account mit der GitHub CLI:

```bash
gh repo create --private --source . --push
```

Folge dem Link im angezeigten Text, um direkt zum erstellten Repository zu gelangen.

### 4. Repository im Browser öffnen

Öffne das Repository auf GitHub.com, um zu prüfen, ob es erfolgreich erstellt wurde.

### 5. ID Token Workflow ausführen

1. Navigiere im Repository oben zum Tab **Actions**.
2. Wähle im linken Menü den Workflow **ID Token Exchange with GCP** aus.
3. Klicke rechts auf **Run workflow** (manueller Start) und gib die `project_number` ein (siehe folgende Notiz).

> [!NOTE]
> Die `project_number` ist ein Pflichtfeld und muss die Projektnummer des Projekts sein,
> das in der [Demo-Umgebung](/demos/00-id-tokens/) erstellt wurde.
> In einer bereitgestellten Umgebung wird der Kursleiter diese Nummer nennen.
> Wird das Lab manuell durchgeführt, muss die Projektnummer aus der Demo-Umgebung ermittelt werden.

Starte nach Eingabe der Projektnummer den Workflow.

### 6. Workflow verfolgen

Klicke in der Liste aktiver Workflow-Runs auf den gerade gestarteten,
dann wähle den einzigen Job **main** aus, um die Details zu sehen.
Es kann nötig sein, die Seite zu aktualisieren, um den neuen Run sehen.

> [!NOTE]
> Dieser Workflow wird sein ID-Token verwenden, um sich in der Google Cloud
> anzumelden und Informationen über Ressourcen abzurufen.
> Die Google Cloud Ressourcen sind so eingestellt, dass nur Repositories,
> die bestimmte Kriterien erfüllen, sie abrufen dürfen.
> Anonyme Nutzer sehen sie nicht.

### 7. Ergebnisse betrachten

Warte bis der Workflow abgeschlossen ist, und aktualisiere dann die Seite erneut. Oben in der Workflow-Detailansicht findest du **Annotations**:

- Die Annotation **ID-Token**, mit einem Base-64 codierten ID-Token (das ebenfalls in seiner Base-64 Form vorliegt)
- Eine Liste aller Buckets im Google Cloud Projekt
- Eine Liste aller Dateien in einem der Buckets

> [!CRITICAL]
> Das ID-Token wird in den Annotationen mit Base-64 codiert angezeigt.
> Da das ID-Token ein temporäres Secret ist, ist das natürlich **unsicher** und sollte
> nicht außerhalb einer geschützten Testumgebung getan werden!
> Dieses Lab-Repository wurde als privates Repository erstellt, sodass die Workflows
> und ihre Logs nur von dir einsehbar sind.
> Jeder, der das ID-Token hat, kann sich als dieser Workflow ausgeben.
> Das `aud`-Feld sollte die Nutzung stark einschränken, aber das Token ist dennoch gültig.

### 8. ID-Token decodieren

Da GitHub Workflows versucht(!) sensible Texte nicht in Logs anzuzeigen wird das ID-Token
in seiner Klartext-Form zensiert. Daher codiert der Workflow das ID-Token mit Base-64,
um es am GitHub-Filter "vorbeizuschmuggeln".

Dies ermöglicht uns, das Token zu kopieren, demonstriert allerdings auch, dass man sich auf
derartige Blacklist-Filter nicht verlassen sollte.

1. Klicke in der Annotation **Get ID Token for this Workflow** auf `Show more`, um den gesamten
Token-Text anzuzeigen und kopiere ihn
2. Öffnet das [vorkonfigurierte CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64('A-Za-z0-9%2B/%3D',true,false)) und füge das Token als Input ein
3. Kopiere das tatsächliche ID-Token im JWT-Format aus dem Output für den nächsten Schritt

> [!NOTE]
> [CyberChef](https://gchq.github.io/CyberChef/) ist ein sehr vielseitiges Werkzeug,
> um Codierungen und andere Datentransformationen vorzunehmen und zu testen.
> Es übertragt die Inputs nirgendwo hin und arbeitet vollständig lokal im Browser,
> ebenso wie [jwt.io](https://jwt.io).

### 9. ID-Token untersuchen

Füge das ID-Token und füge es auf [jwt.io](https://jwt.io/) ein, um die enthaltenen Claims zu analysieren.

Überlege, welche Attribute genutzt werden könnten, um ein Repository, einen Workflow-Run oder andere Details eindeutig zu identifizieren.

### 10. Aufräumen

Kehre in die Lab-Umgebung zur CLI zurück und lösche das Repository:

```bash
gh repo delete
```

Bestätige die Löschung durch Eingabe des Repository-Namens.

### Abschluss

In diesem Lab hast du gesehen, wie ein ID-Token für die Authentifizierung genutzt
und mit einem GitHub Workflow verarbeitet werden kann.
Außerdem hast du gelernt, wie man die Claims eines ID-Tokens analysiert und
daraus Informationen für die Identifikation von Identitäten bekommt.

## Lokale Umgebung bauen

Dieses Lab kann mit Docker selbst nachvollzogen und durchgearbeitet werden.
Voraussetzung ist

1. **Eines** der beiden folgenden Dinge
   1. eine Installation von [`docker`](https://docs.docker.com/engine/install/) (empfohlen)
   2. eine lokale Installation von [`GitHub CLI`](https://github.com/cli/cli#installation) (**beachte den untenstehenden Hinweis!**).
2. Ein Google Cloud Account, um die [Demo-Umgebung](/demos/00-id-tokens/) in Google Cloud aufzubauen

> [!NOTE]
> Für die Nutzung des Labs ohne `docker` ist es nötig, einige Einstellungen
> bzgl. `git` selbst vorzunehmen. `user.name` und `user.email` müssen gesetzt
> werden und der `lab-id-tokens`-Ordner muss als Git-Repository initialisiert werden,
> damit es als Repository gepusht werden kann.
> Nutze diese Variante nur, wenn du mit Git-Einstellungen umgehen und eventuelle Fehler selbst beheben kannst.

### 1. Klone das Repository

```bash
git clone <repository-url>
cd security-by-design/labs/00-id-tokens
```

### 2. Baue den Container

```bash
docker build -t labs/00-id-tokens .
```

### 3. Starten des Containers

```bash
docker run -it --name id-tokens --hostname id-tokens labs/00-id-tokens
```

### Existierenden Container verwenden

Falls der Container bereits existiert:

```bash
docker start -i id-tokens
```

### Container löschen/zurücksetzen

```bash
docker rm id-tokens
```
