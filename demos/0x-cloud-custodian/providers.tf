terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.3.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.7.2"
    }
  }
}

provider "google" {
  region = var.region
}
