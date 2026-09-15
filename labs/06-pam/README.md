# PAM Lab - Anleitung für Studierende

In diesem Lab lernst du den **Privileged Access Manager (PAM)** direkt kennen.
Du übernimmst die Rolle eines Administrators deines Google Cloud-Projekts, beantragst eine zeitlich begrenzte,
genehmigungsbasierte Erweiterung deiner eigenen Berechtigungen und nutzt diesen erweiterten Zugriff, um eine Änderung vorzunehmen.

- [PAM Lab - Anleitung für Studierende](#pam-lab---anleitung-für-studierende)
  - [Schritt 1 - IAM-Seite deines Projekts öffnen](#schritt-1---iam-seite-deines-projekts-öffnen)
  - [Schritt 2 - Zugriffseinschränkung beobachten](#schritt-2---zugriffseinschränkung-beobachten)
  - [Schritt 3 - Temporär erweiterten Zugriff über PAM beantragen](#schritt-3---temporär-erweiterten-zugriff-über-pam-beantragen)
  - [Schritt 4 - Auf Genehmigung warten](#schritt-4---auf-genehmigung-warten)
  - [Schritt 5 - Erweiterten Zugriff nutzen](#schritt-5---erweiterten-zugriff-nutzen)
  - [Schritt 6 - Ergebnis überprüfen](#schritt-6---ergebnis-überprüfen)
  - [Schritt 7 - Ablauf des Zugriffs beobachten](#schritt-7---ablauf-des-zugriffs-beobachten)
  - [Teil 2 - Anfrage deines Dozenten genehmigen](#teil-2---anfrage-deines-dozenten-genehmigen)
    - [Schritt 8 - PAM-Genehmigungswarteschlange öffnen](#schritt-8---pam-genehmigungswarteschlange-öffnen)
    - [Schritt 9 - Anfrage prüfen und genehmigen](#schritt-9---anfrage-prüfen-und-genehmigen)
    - [Schritt 10 - Bestätigen, dass die Berechtigung des Dozenten aktiv ist](#schritt-10---bestätigen-dass-die-berechtigung-des-dozenten-aktiv-ist)

---

## Schritt 1 - IAM-Seite deines Projekts öffnen

1. Öffne die [Google Cloud Console](https://console.cloud.google.com).
2. Stelle im **project picker** ganz oben auf der Seite (neben dem Google Cloud-Logo) sicher, dass dein **eigenes Studierendenprojekt** ausgewählt ist - nicht das deines Dozenten.
3. Klappe im linken Navigationsmenü **IAM & Admin** auf und klicke auf **IAM**.

Du siehst eine Liste der Nutzer und der Rollen, die sie in diesem Projekt haben.

## Schritt 2 - Zugriffseinschränkung beobachten

Sieh dir die Schaltflächenleiste oben in der IAM-Tabelle an. Du wirst feststellen, dass **Grant Access** und **Remove Access** **ausgegraut** sind. Das bedeutet, dass dein Konto momentan keine Berechtigung hat, IAM-Bindungen in diesem Projekt zu ändern. Das ist beabsichtigt, denn diese Berechtigung ist sehr weitreichend und wir folgen dem Prinzip der geringsten Berechtigungen.

Wenn du mit der Maus über die Schaltfläche **Grant Access** fährst, erklärt ein Hinweisbanner, welche Berechtigung fehlt. Es enthält außerdem einen Link **Fix Access**.

## Schritt 3 - Temporär erweiterten Zugriff über PAM beantragen

1. Klicke im Hinweisbanner auf den Link **Fix Access**. Von der rechten Seite des Bildschirms öffnet sich ein Bereich mit der Bezeichnung **Request Temporary Access**.
2. Du siehst eine Berechtigung: **`lab-elevated-access`**. Klicke darauf, um die Details aufzuklappen und zu lesen, was sie gewährt.
3. Wähle eine **duration**, die für die Änderung am Projekt in den folgenden Schritten passend ist.
4. Das Feld **Justification** ist optional; du kannst es für dieses Lab leer lassen. In einer Produktivumgebung ist es natürlich sinnvoll, den Grund für die Erweiterung zu dokumentieren.
5. Klicke auf **Request**.

Jetzt wartest du darauf, dass dein Dozent die Anfrage genehmigt.

> **Tipp:** Um deine Anfrage nachzuverfolgen, gehe im linken Menü zu **IAM & Admin → Privileged Access Manager** und wähle dann den Tab **Grants**. Dort sollte deine Anfrage den Status `Approval Awaited` haben.

## Schritt 4 - Auf Genehmigung warten

Dein Dozent führt ein automatisches Genehmigungsskript aus. Innerhalb weniger Sekunden ändert sich der Status deiner Anfrage.

Aktualisiere regelmäßig die Seite **Grants** (oder die IAM-Seite). Sobald der Status **Active** lautet, fahre mit dem nächsten Schritt fort.

## Schritt 5 - Erweiterten Zugriff nutzen

PAM hat dir nun vorübergehend die Rolle `Project IAM Admin` gewährt:

1. Navigiere im linken Menü zurück zu **IAM & Admin → IAM**.
2. Die Schaltfläche **Grant Access** sollte nun **aktiv** (blau) sein. Falls sie weiterhin ausgegraut ist, aktualisiere die gesamte Seite (`F5` / `Cmd+R`) und warte bis zu einer Minute, bis die Berechtigungen übernommen wurden.
3. Klicke auf **Grant Access**. Rechts öffnet sich ein Bereich.
4. Gib im Feld **New principals** den Account an, den dein Dozent als Eingabe bereitstellt - frage nach, falls er das noch nicht getan hat.
5. Suche im Dropdown **Select a role** nach **Tag Administrator** und wähle die Rolle aus (`roles/resourcemanager.tagAdmin`).
6. Klicke auf **Save**.

## Schritt 6 - Ergebnis überprüfen

Zurück auf der IAM-Seite solltest du nun Folgendes sehen:

- **`admin@sknx.de`** mit der Rolle **Tag Administrator**.
- **Deinen eigenen Nutzer** mit der Rolle **Project IAM Admin** und dem Hinweis _Granted by: PAM_ in derselben Zeile. Dies ist die temporäre Bindung, die PAM erstellt hat.

## Schritt 7 - Ablauf des Zugriffs beobachten

Du musst nichts weiter tun. Wenn die in Schritt 3 gewählte duration abläuft, entfernt PAM die Bindung `Project IAM Admin` automatisch von deinem Konto. Wenn du die IAM-Seite nach Ablauf der Gewährung aktualisierst, siehst du, dass deine erweiterten Berechtigungen verschwunden sind - ohne dass eine manuelle Bereinigung nötig ist.

Dieser automatische Ablauf ist der Kernnutzen von PAM: Du erhältst genau den Zugriff, den du brauchst, genau so lange, wie du ihn brauchst, und mit vollständiger Nachvollziehbarkeit.

---

## Teil 2 - Anfrage deines Dozenten genehmigen

Jetzt sind die Rollen vertauscht. Dein **Dozent** hat eine PAM-Anfrage für dein Projekt gestellt und wartet darauf, dass **du** sie genehmigst. So lernst du die Seite des Genehmigenden im Ablauf kennen.

### Schritt 8 - PAM-Genehmigungswarteschlange öffnen

1. Klappe im linken Navigationsmenü **IAM & Admin** auf und klicke auf **Privileged Access Manager**.
2. Wähle oben auf der Seite den Tab **Approve grants**. Du solltest eine ausstehende Anfrage mit dem Namen der Berechtigung **`lab-elevated-access`** und der E-Mail-Adresse deines Dozenten als Antragsteller sehen.

> [!NOTE]
> Falls noch nichts angezeigt wird, stellt dein Dozent möglicherweise noch Anfragen. Aktualisiere die Seite nach einigen Sekunden.

### Schritt 9 - Anfrage prüfen und genehmigen

1. Klicke auf der rechten Seite der ausstehenden Zeile auf **Approve/Deny**. Ein Detailbereich öffnet sich und zeigt die beantragte Rolle, die beantragte duration und die vom Dozenten angegebene Begründung.
2. Lies die Details durch. In einer realen Umgebung würdest du hier prüfen, ob die Begründung legitim ist, bevor du den erweiterten Zugriff gewährst.
3. Klicke auf **Approve**, um die Anfrage zu genehmigen.

### Schritt 10 - Bestätigen, dass die Berechtigung des Dozenten aktiv ist

1. Navigiere im linken Menü zu **IAM & Admin → IAM**.
2. Scrolle durch die Bindungen und suche **`admin@sknx.de`** (das Konto deines Dozenten).
3. Du solltest die Rolle **Project IAM Admin** mit dem Hinweis _Granted by: PAM_ sehen. Das ist dieselbe temporäre, auditierbare Bindung, die du in Teil 1 erhalten hast, nun für deinen Dozenten.
   1. **Hinweis:** Wie andere IAM-Zuweisungen kann auch diese bis zu einer Minute benötigen, um übernommen und korrekt angezeigt zu werden.

Der Zugriff deines Dozenten läuft am Ende der beantragten duration automatisch ab, genau wie deiner in Schritt 7. Eine manuelle Bereinigung ist nicht nötig.
