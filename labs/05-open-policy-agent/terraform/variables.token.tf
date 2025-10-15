variable "github_token" {
  description = "GitHub token for authentication (https://github.com/settings/tokens). Must have 'repo', 'workflow', 'read:org', 'delete_repo', 'read:discussion' scope."
  type        = string
  nullable    = false
  sensitive   = true
}
