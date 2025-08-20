variable "repository_name" {
  description = "The name of the GitHub repository."
  type        = string
  nullable    = false
  default     = "demo-github-workflows"
}

variable "repository_dir" {
  description = "The directory path for the repository (no leading slash)."
  type        = string
  nullable    = false
  default     = "repository-content"
}

variable "branch_name" {
  description = "The name of the branch to create."
  type        = string
  nullable    = false
  default     = "add-python"
}

variable "github_token" {
  description = "GitHub token for authentication (https://github.com/settings/tokens). Must have 'repo', 'workflow', 'read:org', 'delete_repo', 'read:discussion' scope."
  type        = string
  nullable    = false
}
