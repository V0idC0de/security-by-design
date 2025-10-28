variable "repository_names" {
  description = "The names of the GitHub repositories."
  type        = list(string)
  nullable    = false
}

variable "files" {
  description = "The path to the fileset directory (no leading slash)."
  type        = list(string)
  nullable    = false
  default     = []
}

variable "default_branch" {
  description = "The default branch for the repository."
  type        = string
  nullable    = false
  default     = "development"
}
