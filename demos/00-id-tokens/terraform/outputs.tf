output "project_number" {
  description = "Project Number of the Demo Project. Required for corresponding Lab."
  value       = local.project.number
}

output "project_id" {
  description = "Project ID of the Demo Project."
  value       = local.project.project_id
}

output "allowed_principalset" {
  description = "Principal allowed to list Bucket objects"
  value       = toset(flatten(values(google_project_iam_binding.github-repository)[*].members))
}

output "sample_bucket" {
  description = "Sample Bucket and Files created."
  value = {
    (google_storage_bucket.sample_bucket.name) = [
      for obj in google_storage_bucket_object.sample_file :
      obj.name
    ]
  }
}
