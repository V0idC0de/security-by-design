package github

import rego.v1

# Diese Policy verweigert Terraform-Pläne, die Repositories mit "coffee" im Namen enthalten

deny contains msg if {
    # Hole alle Änderungen an Ressourcen vom Typ github_repository
    resource := input.resource_changes[_]
    resource.type == "github_repository"

    # Prüfe, ob "coffee" im Repository-Namen enthalten ist (Groß-/Kleinschreibung wird per "lower()" ignoriert)
    contains(lower(resource.change.after.name), "coffee")

    # Erstelle eine Fehlermeldung
    msg := sprintf(
        "Repository '%s' enthält das Wort 'coffee', was nicht erlaubt ist",
        [resource.change.after.name]
    )
}
