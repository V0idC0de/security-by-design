resource "google_project_service" "required" {
  for_each = toset([
    "cloudresourcemanager.googleapis.com",
    "iamcredentials.googleapis.com",
    "iam.googleapis.com",
    "sts.googleapis.com",
  ])
  project            = local.project.project_id
  service            = each.key
  disable_on_destroy = false
}
