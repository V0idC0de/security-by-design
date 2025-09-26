locals {
  # Versuche, YAML Inhalte zu laden. Bei Fehlschlag (z.B. wenn die Datei nicht existiert),
  # wird `null` verwendet, was in YAML einer leeren Datei entspricht.
  repositories_yaml = try(yamldecode(file("${path.module}/settings.yaml")), null)

  # `merge()` kombiniert mehrere Maps, akzeptiert allerdings auch `null` als Eingabe.
  # `merge()` akzeptiert `null` als Parameter, behandelt es als leeren Input und gibt immer eine Map zurück.
  # Kurzum ist eine Nebenwirkung von `merge()`, dass `null` sicher zu einer leeren Map korrigiert wird.
  # `coalesce()` tut laut Dokumentation genau das, verlangt allerdings, dass alle Parameter denselben Typ haben.
  # Das ist in diesem Fall aber nicht gegeben, da `null` und `{ }` (leeres Objekt für Terraform) nicht typ-gleich sind.
  repository_names = lookup(merge(local.repositories_yaml), "repositories", [])
}

resource "github_repository" "workflow_lab" {
  for_each = toset(local.repository_names)

  name       = each.key
  visibility = "public"
  auto_init  = true
}

resource "github_branch_default" "default" {
  for_each = toset(local.repository_names)

  repository = github_repository.workflow_lab[each.key].name
  branch     = "main"
  rename     = true
}
