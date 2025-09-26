locals {
  project = var.project_reuse ? one(data.google_project.existing-lab) : one(google_project.managed-lab)
}

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

resource "google_project" "managed-lab" {
  count           = var.project_reuse ? 0 : 1
  name            = "Managed Lab ${one(random_string.suffix).result}"
  project_id      = "${var.project_id}-${one(random_string.suffix).result}"
  folder_id       = var.parent_folder
  deletion_policy = "DELETE"
  billing_account = data.google_billing_account.my_billing_account.id
}

data "google_project" "existing-lab" {
  count      = var.project_reuse ? 1 : 0
  project_id = var.project_id
}


