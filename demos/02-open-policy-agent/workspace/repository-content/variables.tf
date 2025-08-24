variable "github_token" {
  description = "GitHub token for authentication (https://github.com/settings/tokens). No permissions required, since this Repository should only plan, not apply."
  type        = string
  nullable    = false
  sensitive   = true
}
