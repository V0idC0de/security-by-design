variable "project_reuse" {
  description = "Whether to reuse an existing project with the given project_id. If true, the project will not be created or deleted."
  type        = bool
  nullable    = false
  default     = false
}
variable "project_id" {
  description = "The GCP project ID"
  type        = string
  nullable    = false
  default     = "wif-lab"
}

variable "region" {
  description = "The GCP region"
  type        = string
  nullable    = false
  default     = "europe-west4"
}

variable "billing_account_id" {
  description = "The billing account ID to associate with the project (e.g. '01A2B3-C4D5E6-7F8G9H'). If unset, uses the default billing account."
  type        = string
  nullable    = true
  default     = null
}

variable "parent_folder" {
  description = "The parent folder ID under which the project will be created. If unset, the project will be created under the organization root."
  type        = string
  default     = null

  validation {
    condition     = var.parent_folder == null || can(regex("^folders/\\d+$", var.parent_folder))
    error_message = "The parent_folder must be null or in the format 'folders/123456789'."
  }
}

variable "repository_name" {
  description = "Name of the Repository created as part of the Lab for WIF filtering condition."
  type        = string
  nullable    = false
  default     = "lab-id-tokens"
}

variable "enabled" {
  description = "Whether to enable WIF access. Can be set to `false`, to prevent access without destroying resources."
  type        = bool
  nullable    = false
  default     = true
}
