resource "google_iam_workload_identity_pool" "github" {
  project                   = local.project.project_id
  workload_identity_pool_id = "github"
  # Ensure APIs are enabled before creating WIF resources
  depends_on = [google_project_service.required]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  project                            = local.project.project_id
  display_name                       = "Repos in labs/00-id-tokens"
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "lab-id-tokens"
  disabled                           = !var.enabled
  attribute_condition                = "assertion.repository.split(\"/\")[1] == \"${var.repository_name}\""
  attribute_mapping = {
    "google.subject"            = "assertion.sub"
    "attribute.actor"           = "assertion.actor"
    "attribute.aud"             = "assertion.aud"
    "attribute.repository"      = "assertion.repository"
    "attribute.repository_name" = "assertion.repository.split(\"/\")[1]"
  }
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# WIF Permission to allow access to sample Bucket and Project
resource "google_project_iam_binding" "github-repository" {
  for_each = toset(["roles/storage.bucketViewer", "roles/storage.objectViewer"])
  project  = local.project.project_id
  role     = each.key
  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_name/${var.repository_name}"
  ]
}

