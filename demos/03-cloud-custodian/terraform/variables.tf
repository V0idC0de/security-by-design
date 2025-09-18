variable "create_faulty_account" {
  description = "Whether to create a faulty service account to demonstrate policy violations"
  type        = bool
  nullable    = false
  default     = true
}

variable "billing_account_id" {
  description = "The billing account ID to associate with the project (e.g. '01A2B3-C4D5E6-7F8G9H'). If unset, uses the default billing account."
  type        = string
  nullable    = true
  default     = null
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
  nullable    = false
  default     = "c7n-lab"
}

variable "project_reuse" {
  description = "Whether to reuse an existing project with the given project_id. If true, the project will not be created or deleted."
  type        = bool
  nullable    = false
  default     = false
}

variable "region" {
  description = "The GCP region"
  type        = string
  nullable    = false
  default     = "europe-west3"
}

variable "services" {
  description = "The GCP services to enable"
  type        = list(string)
  nullable    = false
  default = [
    # Managing Permissions and Service Accounts via Custodian
    "iam.googleapis.com",
    # Deploy Cloud Functions v1 for Custodian
    "cloudfunctions.googleapis.com",
    # Build Cloud Functions v1
    "cloudbuild.googleapis.com",
    # Cloud Functions v1 require Artifact Registry
    "artifactregistry.googleapis.com",
    # Log Streaming
    "logging.googleapis.com",
    "pubsub.googleapis.com",
  ]
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
