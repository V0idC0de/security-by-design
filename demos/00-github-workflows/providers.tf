terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.6.0" # explizite Version!
    }
  }
}

provider "github" {
  # Keine Token-Angabe nötig, falls via GitHub CLI authentifiziert
  token = var.github_token
}
