# X0 Google Cloud

- [X0 Google Cloud](#x0-google-cloud)
  - [Durchführung](#durchführung)
    - [1. Google Cloud Console öffnen](#1-google-cloud-console-öffnen)
    - [2. Bucket erstellen](#2-bucket-erstellen)
    - [3. Ordner erstellen und Datei hochladen](#3-ordner-erstellen-und-datei-hochladen)
    - [4. Berechtigungen des Buckets prüfen](#4-berechtigungen-des-buckets-prüfen)
    - [5. Service Account erstellen](#5-service-account-erstellen)
    - [6. Berechtigungen für den Service Account vergeben](#6-berechtigungen-für-den-service-account-vergeben)
    - [7. Impersonation-Berechtigung vergeben](#7-impersonation-berechtigung-vergeben)
    - [8. Cloud Shell aktivieren](#8-cloud-shell-aktivieren)
    - [9. Objekt mit dem Service Account herunterladen](#9-objekt-mit-dem-service-account-herunterladen)
      - [9.a Impersonation für die Sitzung aktivieren](#9a-impersonation-für-die-sitzung-aktivieren)
      - [9.b Identität des Service Accounts bestätigen](#9b-identität-des-service-accounts-bestätigen)
      - [9.c Objekt als Service Account herunterladen](#9c-objekt-als-service-account-herunterladen)
      - [9.d Berechtigungsgrenzen testen](#9d-berechtigungsgrenzen-testen)
      - [9.e Impersonation deaktivieren](#9e-impersonation-deaktivieren)
      - [9.f Vergleich: als du selbst löschen](#9f-vergleich-als-du-selbst-löschen)
    - [10. Aufräumen](#10-aufräumen)
    - [Abschluss](#abschluss)

In diesem Lab machst du deine ersten Schritte in der **Google Cloud Console**. Anhand eines
kleinen Szenarios - eine Datei in einem Cloud Storage Bucket, auf die ein **Service Account**
zugreifen soll - lernst du die grundlegende Struktur von Google Cloud (Projekte, Ressourcen, IAM)
sowie die Bedienung der Web Console kennen. Dabei siehst du am eigenen Beispiel, dass Berechtigungen
in der Cloud **granular pro Identität** vergeben werden müssen und nichts automatisch "mitgilt" -
ein zentrales Prinzip von Security by Design.

> [!NOTE]
> Für dieses Lab benötigst du Zugang zu einem Google Cloud Projekt, das von deinem Kursleiter
> bereitgestellt wurde. Es ist kein eigener Google Cloud Account und kein lokales Setup nötig -
> alle Schritte werden ausschließlich im Browser über die Google Cloud Console durchgeführt.

## Durchführung

Die folgenden Schritte gehen davon aus, dass du bereits Zugangsdaten zu einem Google Cloud Projekt
von deinem Kursleiter erhalten hast.

### 1. Google Cloud Console öffnen

Öffne im Browser [console.cloud.google.com](https://console.cloud.google.com) und melde dich mit
den bereitgestellten Zugangsdaten an.

Prüfe oben links über den Projekt-Umschalter (Project Picker), dass das von deinem Kursleiter
genannte Projekt ausgewählt ist. Falls nicht, wähle es dort aus.
Eventuell musst du über das Drop-down Menü oben links im Pop-Up eine **Organisation** auswählen, um das Projekt zu sehen.

> [!NOTE]
> Ein Google Cloud **Projekt** ist die grundlegende Einheit, in der Ressourcen (Buckets,
> Service Accounts, VMs, ...) organisiert werden. Rechte werden typischerweise auf
> Projektebene oder direkt auf einzelnen Ressourcen vergeben - genau das schauen wir uns
> in diesem Lab genauer an.

### 2. Bucket erstellen

Navigiere über das Menü links (Hamburger-Icon) zu **Cloud Storage → Buckets** und klicke auf
**Erstellen** (Create).

1. Vergib einen eindeutigen Namen (Bucket-Namen sind **global** eindeutig - ergänze z.B. deine
   Initialen oder eine Zufallszahl, z.B. `sbd-lab-<eindeutiger name>`).
2. Übernimm bei Standort, Speicherklasse und Zugriffssteuerung die vorgeschlagenen Standardwerte
   (**Einheitliche Zugriffssteuerung / Uniform bucket-level access** sollte aktiv sein - dazu
   mehr in Schritt 4).
3. Klicke auf **Erstellen**.

> [!NOTE]
> **Uniform bucket-level access** bedeutet, dass der Zugriff auf den Bucket ausschließlich über
> **IAM-Rollen** (Identity & Access Management) gesteuert wird (statt über zusätzliche, objektspezifische ACLs).
> Das macht Berechtigungen leichter nachvollziehbar - genau das, was wir in Schritt 4 und 6 prüfen bzw. vergeben.

### 3. Ordner erstellen und Datei hochladen

Öffne den gerade erstellten Bucket und klicke auf **Ordner erstellen**, z.B. mit dem Namen `daten`.

Erstelle lokal auf deinem Rechner eine kleine JSON-Datei, z.B. `geheim.json` mit folgendem Inhalt:

```json
{
  "lab": "google-cloud",
  "hinweis": "Dieses Objekt sollte nur mit expliziter Berechtigung lesbar sein."
}
```

Öffne den Ordner `daten` und lade die Datei über **Hochladen → Dateien hochladen** in den Bucket hoch.

### 4. Berechtigungen des Buckets prüfen

Wechsle im Bucket zum Tab **Berechtigungen** (Permissions).

Sieh dir an, welche Principals (Nutzer, Gruppen, Service Accounts) hier aktuell Zugriff haben.
Vermutlich siehst du nur Rollen, die **vom Projekt geerbt** sind (z.B. deine eigene Owner/Editor-Rolle) -
noch kein einziger Service Account hat gezielt Zugriff auf diesen Bucket.

Das ist der Kernpunkt von IAM in Google Cloud: Zugriff wird **pro Identität** (Nutzer,
Service Account, Gruppe) und **pro Ressource oder Projekt** vergeben. Eine neue Identität hat
standardmäßig **keinerlei Zugriff**, bis ihr explizit eine Rolle zugewiesen wird.

### 5. Service Account erstellen

Navigiere zu **IAM & Verwaltung → Service Accounts** und klicke auf **Service Account erstellen**.

1. Vergib einen Namen, z.B. `lab-reader`.
2. Überspringe den Schritt zur Vergabe von Projektrollen (Felder leer lassen / "Fertig" klicken).
3. Klicke auf **Fertig**.

Der neue Service Account hat nun eine E-Mail-Adresse in der Form
`lab-reader@<projekt-id>.iam.gserviceaccount.com`, aber - wie in Schritt 4 beobachtet - noch
**keinerlei Berechtigungen**.

> [!NOTE]
> Ein **Service Account** ist eine Identität für Anwendungen/Workloads statt für Menschen. Es wird
> genutzt, wenn ein Skript, ein Server oder eine CI/CD-Pipeline (statt eines Menschen) auf
> Google Cloud Ressourcen zugreifen soll.

### 6. Berechtigungen für den Service Account vergeben

Kehre zu deinem Bucket zurück, öffne wieder den Tab **Berechtigungen** und klicke auf
**Zugriff gewähren** (Grant Access).

1. Trage als neuen Principal die E-Mail-Adresse deines Service Accounts ein.
2. Weise die Rolle **Storage Object Viewer** zu.
3. Speichern.

> [!NOTE]
> Beachte, wie gezielt diese Rolle ist: Der Service Account darf nun **Objekte lesen**, aber z.B.
> keine Objekte löschen, keine neuen Buckets erstellen oder Berechtigungen ändern. Das ist das
> Prinzip der **geringsten Rechte** (Least Privilege) in der Praxis.

### 7. Impersonation-Berechtigung vergeben

Um später als der Service Account zu handeln, brauchst du **keinen Schlüssel** - stattdessen kannst
du den Service Account **impersonieren** (kurzzeitig "zu Service Account werden"), sofern dir das explizit erlaubt wurde.

Öffne **IAM & Verwaltung → Service Accounts**, klicke auf `lab-reader` und wechsle zum Tab
**Berechtigungen** (Permissions) **des Service Accounts selbst** (nicht des Buckets!).

1. Klicke auf **Zugriff gewähren** (Grant Access).
2. Trage als neuen Principal deine eigene E-Mail-Adresse (dein Login) ein.
3. Weise die Rolle **Service Account Token Creator** (`roles/iam.serviceAccountTokenCreator`) zu.
4. Speichern.

> [!NOTE]
> Auch Impersonation ist eine gezielt vergebene Berechtigung **auf dem Service Account**, nicht
> auf dem Bucket. Damit gibt es zwei getrennte Berechtigungsebenen: Wer darf diesen Service Account
> _impersonaten/werden_ (Schritt 7, hier) und was darf dieser Service Account dann _tun_ (Schritt 6, Zugriff auf
> den Bucket). Beide Rollen müssen unabhängig voneinander vergeben werden.

### 8. Cloud Shell aktivieren

Klicke oben rechts in der Console auf das **Cloud Shell**-Symbol (`>_`) und warte, bis die Shell
bereitgestellt wurde.

> [!NOTE]
> Cloud Shell stellt dir eine temporäre, kleine VM mit vorinstallierten Tools (u.a. `gcloud`)
> bereit, direkt im Browser. Standardmäßig ist sie mit **deiner eigenen** Nutzeridentität
> angemeldet - mit der du als Projekt-Owner ohnehin auf alles zugreifen könntest. Im nächsten
> Schritt wechseln wir bewusst zur Identität des Service Accounts, um wirklich dessen (begrenzte)
> Berechtigungen zu testen.

### 9. Objekt mit dem Service Account herunterladen

Statt eines Schlüssels nutzen wir jetzt **Impersonation**: `gcloud` besorgt sich dabei über deine
eigene, bereits angemeldete Identität ein kurzlebiges Zugriffstoken für den Service Account - ganz
ohne heruntergeladene Zugangsdaten.

#### 9.a Impersonation für die Sitzung aktivieren

Setze dazu in Cloud Shell die Impersonation für die aktuelle Sitzung.

> [!WARNING]
> Wenn du diesen Befehl ausführst, denke daran ihn mit Schritt 9.e wieder rückgängig zu machen
> wenn du hier fertig bist. Ansonsten werden zukünftige Kommandos weiterhin die Impersonation nutzen,
> was ggf. zu Fehlern führen kann.

```bash
gcloud config set auth/impersonate_service_account lab-reader@<projekt-id>.iam.gserviceaccount.com
```

Dieser Befehl bewirkt, dass `gcloud` ab sofort **vor jedem** folgenden Befehl zunächst die
Identität des angegebenen Service Accounts annimmt (über ein kurzlebiges Token) und den Befehl
dann **in dessen Namen** ausführt - so lange, bis du die Impersonation wieder deaktivierst
(Schritt 9.e).

> [!NOTE]
> `gcloud`-Befehle akzeptieren dazu alternativ auch das Flag `--impersonate-service-account=...`
> direkt an einem einzelnen Befehl, um nur für diesen eine Impersonation auszuführen.

#### 9.b Identität des Service Accounts bestätigen

Frage Google Cloud, welche Identität aktuell tatsächlich für Anfragen verwendet wird - der
**Caller Identity Check**:

```bash
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$(gcloud auth print-access-token)"
```

Im Feld `email` der Ausgabe siehst du `lab-reader@<projekt-id>.iam.gserviceaccount.com` - du
handelst jetzt tatsächlich als der Service Account, nicht mehr als du selbst.

#### 9.c Objekt als Service Account herunterladen

Lade nun das Objekt herunter:

```bash
gcloud storage cp gs://<dein-bucket-name>/daten/geheim.json .
cat geheim.json
```

Der Download sollte erfolgreich sein - **nur** weil in Schritt 6 gezielt die passende
Berechtigung vergeben wurde. Ohne diesen Schritt hätte der Befehl mit einem
`403 Permission denied` fehlgeschlagen, obwohl du selbst als Projekt-Owner den Bucket problemlos
sehen könntest.

#### 9.d Berechtigungsgrenzen testen

Probiere diesen Befehl aus, **der fehlschlagen wird**, da der Service Account keine Berechtigungen hat
um das Objekt zu löschen - dein eigener Account könnte diese Aktion durchführen:

```bash
# Dieser Befehl wird fehlschlagen
gcloud storage rm gs://<dein-bucket-name>/daten/geheim.json
```

#### 9.e Impersonation deaktivieren

Schalte die Impersonation danach wieder aus, um in Cloud Shell wieder als du selbst zu handeln
und überprüfe dies mit dem `/tokeninfo`-Endpunkt.

```bash
gcloud config unset auth/impersonate_service_account
curl -s "https://oauth2.googleapis.com/tokeninfo?access_token=$(gcloud auth print-access-token)"
```

#### 9.f Vergleich: als du selbst löschen

Wiederhole jetzt den Befehl zum Löschen des Objekts - er läuft nun wieder als dein persönlicher Account:

```bash
gcloud storage rm gs://<dein-bucket-name>/daten/geheim.json
```

> [!INFO]
> Da kein Schlüssel involviert war, gibt es auch kein langlebiges Secret, das gestohlen werden
> oder versehentlich in einem Repository landen könnte - das Zugriffstoken der Impersonation ist
> nur kurzzeitig gültig. Genau dieses Prinzip - Zugriff ohne dauerhafte, statische Zugangsdaten -
> vertiefen spätere Labs mit ID-Tokens und Workload Identity Federation.

### 10. Aufräumen

Räume die erstellten Ressourcen wieder auf:

1. Lösche in **IAM & Verwaltung → Service Accounts** den Service Account `lab-reader`.
2. Lösche in **Cloud Storage → Buckets** deinen erstellten Bucket (inkl. Inhalt).

### Abschluss

In diesem Lab hast du dich zum ersten Mal durch die Google Cloud Console bewegt und dabei
Folgendes gelernt:

- Navigation durch die Google Cloud Console: Projekte, Cloud Storage Buckets, Service Accounts
  und Cloud Shell.
- Berechtigungen in der Cloud gelten **pro Identität** - ein neuer Service Account hat
  standardmäßig nichts, und selbst kleine Aufgaben (ein Objekt lesen) erfordern eine gezielte,
  geprüfte Rechtevergabe.
- Für den Zugriff braucht es **keinen** heruntergeladenen Schlüssel: Mit **Impersonation** und
  einem expliziten Caller-Identity-Check hast du nachvollzogen, als welche Identität `gcloud`
  gerade tatsächlich handelt.
- Dieses Prinzip - Zugriff ohne dauerhafte, statische Zugangsdaten - vertiefen die folgenden
  Labs weiter, u.a. mit kurzlebigen ID-Tokens und Workload Identity Federation.
