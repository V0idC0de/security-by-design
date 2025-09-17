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
