output "region" {
  description = "The GCP region used for the demo."
  value       = var.region
}

output "project" {
  description = "The GCP project resource used for the demo."
  value       = local.project
}

output "project_id" {
  description = "The GCP project ID created for the demo"
  value       = local.project.project_id
}

output "custodian_service_account_email" {
  description = "The email of the service account created for Cloud Custodian"
  value       = google_service_account.custodian.email
}

# Local file for easier access to output variables
resource "local_file" "output" {
  filename = "${path.module}/outputs.json"
  content = jsonencode({
    project                         = local.project
    project_id                      = local.project.project_id
    region                          = var.region
    custodian_service_account_email = google_service_account.custodian.email
  })
  file_permission = "0644"
}
