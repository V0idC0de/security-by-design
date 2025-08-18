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
