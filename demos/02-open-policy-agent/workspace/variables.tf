variable "repository_name" {
  description = "The name of the GitHub repository."
  type        = string
  nullable    = false
  default     = "demo-open-policy-agent"
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
  default     = "add-repositories"
}
