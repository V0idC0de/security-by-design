locals {
  enabled_services = compact([
    "compute.googleapis.com",
    "storage.googleapis.com",
  ])
}

resource "google_project_service" "enabled" {
  for_each = toset(local.enabled_services)
  project  = local.project.project_id
  service  = each.key
}
