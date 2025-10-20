package github

import rego.v1

# Definiere die deny-Regel, um Verstöße zu identifizieren
deny contains msg if {
    # Hole alle Änderungen an Ressourcen vom Typ github_repository
    resource := input.resource_changes[_]
    resource.type == "github_repository"

    # Prüfe, ob die Sichtbarkeit des Repositories auf 'public' gesetzt ist
    resource.change.after.visibility == "public"

    # Erzeuge eine Fehlermeldung mit dem Namen des Repositories
    msg := sprintf("Repository '%s' hat die Sichtbarkeit 'public'. Nutze 'private'.", [resource.address])
}
