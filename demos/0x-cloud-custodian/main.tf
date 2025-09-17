data "google_client_openid_userinfo" "me" {}

data "google_billing_account" "my_billing_account" {
  billing_account = var.billing_account_id
  display_name    = var.billing_account_id != null ? null : "My Billing Account"
  open            = true
  lookup_projects = false
}

resource "random_string" "suffix" {
  count   = var.project_reuse ? 0 : 1
  length  = 3
  upper   = false
  lower   = true
  numeric = true
  special = false
}

resource "google_project" "demo" {
  count           = var.project_reuse ? 0 : 1
  name            = "Cloud Custodian Lab ${one(random_string.suffix).result}"
  project_id      = "${var.project_id}-${one(random_string.suffix).result}"
  folder_id       = var.parent_folder
  deletion_policy = "DELETE"
  billing_account = data.google_billing_account.my_billing_account.id
}

data "google_project" "existing-demo" {
  count      = var.project_reuse ? 1 : 0
  project_id = var.project_id
}

locals {
  project = var.project_reuse ? one(data.google_project.existing-demo) : one(google_project.demo)
}

resource "google_project_service" "enabled_services" {
  for_each = toset(var.services)
  project  = local.project.project_id
  service  = each.value
}

resource "google_service_account" "custodian" {
  account_id   = "svc-custodian-fn"
  display_name = "Cloud Custodian Function Service Account"
  project      = local.project.project_id
}

# Allow impersonation of the Custodian Service Account for local execution as that account
resource "google_service_account_iam_binding" "impersonation" {
  service_account_id = google_service_account.custodian.name
  role               = "roles/iam.serviceAccountTokenCreator"
  members = [
    # Determine if the user is a service account or a user account
    endswith("gserviceaccount.com", data.google_client_openid_userinfo.me.email) ?
    "serviceAccount:${data.google_client_openid_userinfo.me.email}" :
    "user:${data.google_client_openid_userinfo.me.email}"
  ]
}

resource "google_project_iam_binding" "serviceAccountAdmin" {
  project = local.project.project_id
  role    = "roles/iam.serviceAccountAdmin"
  members = ["serviceAccount:${google_service_account.custodian.email}"]
}

resource "google_service_account" "faulty" {
  count        = var.create_faulty_account ? 1 : 0
  account_id   = "barista-bot"
  display_name = "Automated Barista for the Coffee Machine"
  project      = local.project.project_id
}
