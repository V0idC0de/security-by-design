# GitHub Login

Einige Labs benötigen eine Anmeldung bei GitHub. Um das zu tun, ist es am praktischsten
die **GitHub CLI** (`gh`) zu nutzen.

Diese ermöglicht sehr einfache Interaktion mit GitHub und stellt auch Zugangsdaten für andere
Programme auf dem System zur Verfügung, wie z.B. Terraform.

Zum Login, befolge diese Schritte in deiner Umgebung:

```bash
# delete_repo ist als zusätzliche Berechtigung nötig, um am Ende aufzuräumen
gh auth login -s delete_repo
```

Wähle der Reihe nach die Optionen:

1. `GitHub.com`
2. `HTTPS` auf die Frage der Verbindungsart (außer du weißt, was du tust und möchtest lieber `SSH`)
3. `Y` auf die Frage "Authenticate Git with your GitHub Credentials"
4. `Login with web browser` auf die Frage, welche Anmeldemethode genutzt werden soll

Kopiere den gezeigten Code, der in etwa so aussieht: `ABCD-EFGH`
Drücke `ENTER`, um zu versuchen die Website zur Anmeldung zu öffnen.
In der Laborumgebung bzw. innerhalb von Docker wird dies fehlschlagen.
Es per `ENTER` zu versuchen ist trotzdem nötig.

Besuche anschließend die gezeigte Adresse manuell.
Melde dich ggf. bei GitHub an, trage den Code auf der Website ein und bestätige die Anmeldung.

GitHub CLI ist jetzt einsatzbereit. Dieser Schritt muss üblicherweise nicht wiederholt werden,
bzw. nur dann, wenn die GitHub CLI explizit dazu auffordert.

## Token extrahieren

Sollte das GitHub Access Token jemals für etwas spezielles benötigt werden,
kann es mit `gh auth token` angezeigt werden.

Das ist für Terraform allerdings nicht nötig.
