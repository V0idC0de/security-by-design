variable "project_id" {
  description = "The GCP project ID"
  type        = string
  nullable    = false
  default     = "managed-lab"
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

variable "project_reuse" {
  description = "Whether to reuse an existing project with the given project_id. If true, the project will not be created or deleted."
  type        = bool
  nullable    = false
  default     = false
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

variable "machine" {
  description = "The machine settings for the compute instance."
  type = object({
    type             = optional(string, "e2-standard-2")
    disk_auto_delete = optional(bool, true)
    disk_size_gb     = optional(number)
    disk_type        = optional(string, "pd-balanced")
    username         = optional(string, "janitor")
  })
  nullable = false
  default  = {}
}

variable "machine_state" {
  description = "The desired state of the machine after creation. Can be 'RUNNING', 'SUSPENDED', or 'TERMINATED'."
  type        = string
  nullable    = false
  default     = "RUNNING"

  validation {
    condition     = contains(["RUNNING", "SUSPENDED", "TERMINATED"], upper(var.machine_state))
    error_message = "The machine_state must be either 'RUNNING', 'SUSPENDED', or 'TERMINATED'."
  }
}

variable "dns_name" {
  description = "Subdomain of duckdns.org to use for the VM's FQDN. If unset, no record at DuckDNS will be created/refreshed. This name must be registered at DuckDNS beforehand!"
  type        = string
  nullable    = true
  default     = null

  validation {
    condition     = var.dns_name == null || can(regex("^[a-zA-Z0-9-]{3,64}$", var.dns_name))
    error_message = "The dns_name must be a valid subdomain (e.g. 'example') without any dots."
  }
}

variable "duckdns_token" {
  description = "The token for the DuckDNS API. Required if dns_name is set."
  type        = string
  nullable    = true
  default     = null
  sensitive   = true

  validation {
    condition     = var.duckdns_token == null || can(regex("^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", var.duckdns_token))
    error_message = "Token for DuckDNS doesn't seem to be a valid UUID format, but that would be expected."
  }
}
