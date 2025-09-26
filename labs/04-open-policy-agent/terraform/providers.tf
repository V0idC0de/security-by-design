terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "6.6.0" # explizite Version!
    }
  }
}

provider "github" {
  token = var.github_token
}
