# 07 Software Bill of Materials (SBOM)

- [07 Software Bill of Materials (SBOM)](#07-software-bill-of-materials-sbom)
  - [Durchführung](#durchführung)
    - [1. Betrachte das Setup](#1-betrachte-das-setup)
    - [2. Untersuche das Beispielprojekt](#2-untersuche-das-beispielprojekt)
    - [3. Erzeuge eine SBOM](#3-erzeuge-eine-sbom)
    - [4. Untersuche die transitiven Dependencies](#4-untersuche-die-transitiven-dependencies)
    - [5. Aufgabe 1: Prüfe zwei bekannte Schwachstellen](#5-aufgabe-1-prüfe-zwei-bekannte-schwachstellen)
    - [6. Aufgabe 2: Scanne die SBOM auf Vulnerabilities](#6-aufgabe-2-scanne-die-sbom-auf-vulnerabilities)
    - [7. Aufgabe 3: Untersuche die Betriebssystempakete](#7-aufgabe-3-untersuche-die-betriebssystempakete)
    - [Abschluss](#abschluss)

Du untersuchst ein kleines Python-Projekt mit dem Paket **Requests** als Abhängigkeit und erzeugst mit **Syft** eine SBOM (Software Bill of Materials).
Darin prüfst du zwei bekannte CVEs anhand der Paketversionen. Anschließend scannt **Grype** dieselbe SBOM
auf weitere bekannte Schwachstellen. Zum Schluss erweiterst du den Blick auf die Pakete des Betriebssystems.

> [!CAUTION] Dieses Lab verwendet absichtlich ältere Paketversionen und einen eingefrorenen Datenbankstand.
> Verwende diese Umgebung nicht als Vorlage für produktive Anwendungen.

## Durchführung

Führe die folgenden Befehle in der Lab-Shell der bereitgestellten Umgebung aus.

### 1. Betrachte das Setup

```bash
tree -L 2
cd lab-project
```

Der Ordner `lab-project` enthält etwas Beispielcode in `app.py` und `requirements.txt`,
die Dependencies auflistet.
Der Ordner `venv` enthält die vorbereitete **virtuelle Python-Umgebung** mit den installierten Dependencies aus `requirements.txt`.
`tree -L 2` zeigt die Projektstruktur bis zur zweiten Ebene, sodass der tiefe `venv`-Ordner nicht vollständig gelistet wird.

### 2. Untersuche das Beispielprojekt

```bash
batcat app.py requirements.txt
```

`app.py` ist eine kleine Funktion, die HTTP-Requests vorbereitet - jedoch **nicht sendet** (dies ist später wichtig).
Dazu wir `requests` gleich in Zeile 1 importiert. In `requirements.txt` steht das Paket als `requests==2.32.5`:
Das ist die **direkte Dependency**. Merke dir, dass hier ein Paket als Dependency aufgeführt ist und vergleiche dies später mit der SBOM.

### 3. Erzeuge eine SBOM

**Syft** ist ein SBOM-Generator. Es untersucht hier `venv`, weil dort alle Dependencies des Projekts
installiert sind, nicht nur die Einträge in `requirements.txt`.

```bash
syft venv -o cyclonedx-json=sbom.json
```

`-o cyclonedx-json=sbom.json` schreibt die SBOM im **CycloneDX**-Format (ein JSON-Schema) nach `sbom.json`.

Das folgende `jq`-Kommando erzeugt eine besser lesbare Version der `sbom.json`, indem es einige große Listen ohne Mehrwert für dieses Lab entfernt.

Betrachte nun die SBOM-Datei und die enthaltenen Informationen, besonders die Elemente im Element `components` (Zeile 26ff in `sbom-clean.json`):

```bash
jq 'del(.components[].properties)' sbom.json > sbom-clean.json

batcat sbom-clean.json
# Verlasse die Scroll-Ansicht mit "q", wenn du genug gesehen hast
```

- `components`: Pakete mit Namen, Version und weiteren Metadaten.
- `name` und `version`: Paketname und installierte Version.
- `purl`: Eine **Package URL** mit Ökosystem, Paketname und Version, etwa `pkg:pypi/urllib3@2.2.1`.

### 4. Untersuche die transitiven Dependencies

**jq** filtert hier die JSON-Daten. Der folgende Filter zeigt aus `components` für jedes Paket
nur `name` und `version`, um eine kompakte Übersicht zu erzeugen.

```bash
# Zeigt Name und Version jedes identifizierten Pakets
jq '.components[] | {name, version}' sbom.json
```

Vergleiche die Ausgabe mit deiner Notiz aus Schritt 2: Du siehst **fünf Pakete**, obwohl
`requirements.txt` nur Requests nennt. Die vier zusätzlichen Pakete benötigt Requests selbst;
sie werden automatisch mitinstalliert. Diese **transitiven Dependencies** gehören zur Anwendung,
ohne direkt in `requirements.txt` aufgeführt zu sein!

### 5. Aufgabe 1: Prüfe zwei bekannte Schwachstellen

Nehmen wir nun folgendes an: Dein Team bekommt zwei Sicherheitsmeldungen. Prüfe anhand deiner SBOM und der Tabelle:
**Ist das Paket enthalten, und liegt seine Version im betroffenen Bereich?**

| Meldung | Paket | Betroffener Versionsbereich | Kurzbeschreibung |
| --- | --- | --- | --- |
| [CVE-2024-37891](https://github.com/advisories/GHSA-34jh-p97f-mpxf) | `urllib3` | `< 1.26.19` oder `>= 2.0.0` und `< 2.2.2` | Unter bestimmten Bedingungen wird ein `Proxy-Authorization`-Header bei einem Redirect an einen anderen Origin weitergegeben. |
| [CVE-2024-3651](https://github.com/advisories/GHSA-jjg7-2v4v-x38h) | `idna` | `< 3.7` | Speziell präparierte Eingaben für `idna.encode()` können übermäßigen Ressourcenverbrauch und damit einen Denial of Service auslösen. |

Alle nötigen Angaben stehen in der Tabelle; die Links dienen als Quellen.

```bash
# Suche beide Pakete und ihre Versionen in der erzeugten SBOM
jq '.components[] | select(.name == "urllib3") | {name, version, type, author, purl}' sbom.json

jq '.components[] | select(.name == "idna") | {name, version, type, author, purl}' sbom.json
```

Halte für jede Meldung kurz fest:

1. Liegt diese Version im betroffenen Bereich?
2. Ist das Paket eine direkte oder eine transitive Dependency?

<!-- markdownlint-disable MD033 -->
<details>
<summary>Erwartete Ergebnisse anzeigen</summary>

- **urllib3 2.2.1:** Über Requests enthalten, also transitiv. Die Version liegt zwischen `2.0.0`
  einschließlich und `2.2.2` ausschließlich. Eine von **CVE-2024-37891 betroffene Paketversion** ist vorhanden.
- **idna 3.7:** Ebenfalls transitiv enthalten. Die Version liegt nicht im Bereich `< 3.7`.
  Von **CVE-2024-3651** ist diese Paketversion laut Versionsabgleich nicht betroffen.

Eine betroffene Paketversion beweist keine konkrete Ausnutzbarkeit. Nötige Vorbedingungen für eine Ausnutzung könnten fehlen. Die CVE für `urllib3` betrifft z.B. Header und Weiterleitungen beim Durchführen von HTTP-Requests. Doch diese Applikation sendet gar keine Requests, sondern bereitet diese lediglich vor. Ein klassischer Fall von "not applicable", der das Risiko stark senkt.

Umgekehrt ist `idna 3.7` natürlich nicht pauschal frei von Schwachstellen, nur weil hier keine weiteren gelistet sind.

> [!CAUTION]
> Im Zweifel wird natürlich erstmal eine Ausnutzbarkeit angenommen. Auch sollten mitigierende Faktoren die Behebung/Patch nicht langfristig behindern.
> Eine zukünftige Konfigurationsänderung könnte die nötigen Vorbedingungen unerwartet schaffen.
> Diese Abwägung über Risiko und mitigierende Maßnahmen unterstützt bei **Risikoabwägung und Priorisierung** - die Frage ist nicht **ob** gepatcht wird, sondern **wann** und **wo zuerst**.

</details>
<!-- markdownlint-enable MD033 -->

### 6. Aufgabe 2: Scanne die SBOM auf Vulnerabilities

Bisher hast du bekannte CVEs gezielt geprüft. **Grype** gleicht die Paketnamen und Versionen deiner SBOM mit einer lokalen **Vulnerability Database** ab.
Welche bekannten Schwachstellen findet es für alle enthaltenen Pakete?

```bash
# Zeigt den vorbereiteten Datenbankstand; führt kein Update aus
grype db status

# Scannt genau die erzeugte SBOM
grype sbom:sbom.json
```

Finde **CVE-2024-37891** wieder und vergleiche den Treffer mit deiner Einordnung aus Aufgabe 1.

Beachte auch den Treffer für `idna`: Er betrifft eine andere CVE als **CVE-2024-3651**. Obwohl unsere Version von `idna` also für die gesuchte CVE nicht anfällig ist, gibt es eine andere relevante CVE.

Grype verwendet deine SBOM und **berücksichtigt betroffene Versionsbereiche automatisch**.
Schwachstellen, die laut Datenbank nur andere Versionen betreffen, erscheinen nicht als Treffer.
Der Scan prüft nicht die konkrete Ausnutzbarkeit deiner Anwendung.

### 7. Aufgabe 3: Untersuche die Betriebssystempakete

Bisher hast du nur die fünf Python-Pakete der Anwendung betrachtet. Doch auch das Betriebssystem
bringt Pakete mit, beispielsweise die Shell und Systembibliotheken. Welche zusätzlichen Komponenten
und bekannten Schwachstellen kommen dadurch hinzu?

Erzeuge nun eine zweite SBOM. `dir:/` untersucht das Dateisystem.
`--override-default-catalogers dpkg-db-cataloger` und `--select-catalogers '-file'` beschränken den Suchlauf auf Pakete aus Debians Paketdatenbank.
Die Ausschlüsse lassen virtuelle Verzeichnisse wie `/proc` und andere unwichtige aus.

```bash
# Einige Warnungen über Zugriffsrechte sind bei diesem Kommando erwartet und unproblematisch
syft dir:/ --override-default-catalogers dpkg-db-cataloger \
  --select-catalogers '-file' \
  --exclude './proc/**' \
  --exclude './sys/**' \
  --exclude './dev/**' \
  --exclude './root/**' \
  -o cyclonedx-json=sbom-os.json
```

Nun vergleiche die Anzahl gefundener Pakete. Zuerst wird die Python-Anwendung, dann die aus dem Betriebssystem gelistet.

```bash
jq '.components | length' sbom.json sbom-os.json
```

Zuletzt nun die Anzahl der Findings für die Betriebssystempakete.

```bash
grype sbom:sbom-os.json -o json | jq '.matches | length'
```

Wir leiten hier bewusst den Output via `-o json` als JSON an `jq` weiter, um mit `.matches | length` die Findings zu zählen.
Eine Liste aller Findings ist deutlich zu groß.

Du siehst deutlich mehr Pakete als in der Anwendungs-SBOM und erheblich mehr Findings.
Das zeigt uns: **Nicht nur die Dependencies der Anwendung, sondern auch das Betriebssystem gehört zum Sicherheitsbild.**

Auch hier ist ein Treffer noch kein Nachweis einer konkreten Ausnutzbarkeit.

> [!TIP]
> Der gewählte Filter erfasst nur Debian-Pakete, nicht die Python-Umgebung oder separat installierte Tools.
> Daraus entsteht eine zunehmende Komplexität bei Systemen die viel installierte Software für mehrere Aufgaben aus diversen Quellen installieren.
> Dies motiviert minimale Systeme mit kleinem Aufgabenbereich.

### Abschluss

Die **SBOM beschreibt das Inventar**; Grype (oder ähnliche Software) ergänzt bekannte Schwachstellen aus seiner Datenbank.

Die SBOM-Dateien bleiben im Projektordner. `sbom.json` beschreibt die **Python-Pakete der Anwendung**,
`sbom-os.json` die **Debian-Pakete des Systems**. Beide Perspektiven sind nötig, um bekannte
Schwachstellen nicht nur in den Dependencies der Anwendung, sondern auch in der Laufzeitumgebung zu erkennen.

Zum Abschluss zeigte das Lab nun Folgendes:

- `sbom.json` enthält die fünf Pakete mit ihren Versionen.
- Du kannst erklären, warum `urllib3` und `idna` fehlen würden, wenn du nur direkte Requirements betrachtest.
- Du kannst die unterschiedlichen Ergebnisse der beiden CVE-Prüfungen begründen.
- Du hast die SBOM mit Grype gescannt und kannst einen Treffer erklären.
- Du hast die Betriebssystempakete separat erfasst, ihre Findings gezählt und kannst erklären, warum auch sie berücksichtigt werden müssen.
- Du unterscheidest zwischen vorhandener Komponente, betroffener Version und konkreter Ausnutzbarkeit.
