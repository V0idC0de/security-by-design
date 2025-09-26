# GitHub Personal Access Tokens (PAT)

## Erstellung eines Tokens für deinen Account

Um ein **Personal Access Token (PAT)** bei GitHub mit den nötigen Berechtigungen für die Labs zu erstellen,
folge diesen Schritten:

1. Besuche <https://github.com/settings/tokens>
2. Klicke auf **Generate new token**, dann auf **Generate new token (classic)**
3. Gib einen sprechenden Namen für das Token ein und wähle die gewünschte Gültigkeitsdauer aus - z.B. 60 Tage.
4. Wähle für die Labs folgende Berechtigungen aus:
   1. `repo`: Full control of private repositories
   2. `workflow`: Update GitHub Action workflows
   3. `read:org`: Read org and team membership, read org projects
   4. `delete_repo`: Delete repositories
   5. `read:discussion`: Read team discussions

Speichere den Token nach der Erstellung sicher ab, da er nur einmal angezeigt wird.
