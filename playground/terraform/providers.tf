terraform {
  required_version = ">= 1.11"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.3.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "4.1.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
    local = {
      source  = "hashicorp/local"
      version = "2.5.3"
    }
    http = {
      source  = "hashicorp/http"
      version = "3.5.0"
    }
    netcup = {
      source  = "rixlhq/netcup"
      version = "~> 1.2.1"
    }
  }
}

provider "tls" {}

provider "google" {
  region = var.region
}

# Configure the following environment variables or Terraform variables, if DNS should be configured.
# - NETCUP_API_KEY
# - NETCUP_API_PASSWORD
# - NETCUP_CUSTOMER_NUMBER
provider "netcup" {
  api_key         = try(var.netcup.api_key, null)
  api_password    = try(var.netcup.api_password, null)
  customer_number = try(var.netcup.customer_number, null)
}
