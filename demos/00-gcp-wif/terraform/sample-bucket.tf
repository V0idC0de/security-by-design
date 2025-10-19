resource "google_storage_bucket" "sample_bucket" {
  name                        = "${local.project.project_id}-bucket-${random_string.bucket_suffix.result}"
  location                    = var.region
  project                     = local.project.project_id
  force_destroy               = true
  uniform_bucket_level_access = true
}

resource "random_string" "bucket_suffix" {
  length  = 3
  upper   = false
  lower   = true
  numeric = true
  special = false
}

resource "google_storage_bucket_object" "sample_file" {
  for_each = toset(["hello.txt", "data.json", "info.csv"])
  name     = each.key
  bucket   = google_storage_bucket.sample_bucket.name
  content  = "Hello, world!"
}
