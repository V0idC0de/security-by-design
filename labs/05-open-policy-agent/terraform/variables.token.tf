variable "github_token" {
  description = "GitHub token for authentication. Must have additional 'delete_repo' scope."
  type        = string
  nullable    = false
  sensitive   = true
}
