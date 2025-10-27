resource "github_repository" "workflow_lab" {
  name = var.repository_name

  # "public" Visibility ist notwendig, um die Branch Protection nutzen zu können,
  # wenn der Nutzer einen GitHub Free Account hat - andersfalls sind die deaktiviert.
  visibility = "public"
  auto_init  = true # Initialisiert mit README, wichtig für Branch Creation

  delete_branch_on_merge = true
  has_discussions        = false
  has_downloads          = false
  has_issues             = false
  has_projects           = false
  has_wiki               = false
}

resource "github_branch_protection" "default" {
  repository_id = github_repository.workflow_lab.node_id
  pattern       = github_repository.workflow_lab.default_branch

  allows_force_pushes = false
  allows_deletions    = false
  enforce_admins      = true

  required_status_checks {
    strict   = true
    contexts = sort(local.ci_jobs)
  }
  depends_on = [github_repository_file.main]
}

resource "github_actions_secret" "GITHUB_PAT" {
  repository      = github_repository.workflow_lab.name
  secret_name     = "GH_PAT"
  plaintext_value = var.github_token
}
locals {
  # As people might fiddle with the inner Terraform code contained in `repository-content`,
  # it's better to explicitly define the files we want to upload.
  # Otherwise, people may place files in that `repository-content` directory,
  # which are then accidentally uploaded to GitHub.
  files_to_upload = [
    ".github/workflows/ci.yml",
    "policy/no-coffee.rego",
    "policy/no-public-repositories.rego",
    "main.tf",
    "providers.tf",
    "settings.yaml",
    "variables.tf",
    ".terraform.lock.hcl"
  ]
  repo_files = {
    for f in local.files_to_upload :
    f => "${path.module}/${var.repository_dir}/${f}"
  }

  ci_yaml = yamldecode(file("${path.module}/${var.repository_dir}/.github/workflows/ci.yml"))
  ci_jobs = values(local.ci_yaml.jobs)[*].name
}

resource "github_repository_file" "main" {
  for_each   = local.repo_files
  repository = github_repository.workflow_lab.name
  branch     = github_repository.workflow_lab.default_branch
  file       = each.key
  # Commit empty `repositories.yaml` at first - then commit a change with its actual content to different branch
  content             = each.key == "settings.yaml" ? "" : file(each.value)
  commit_message      = "Add ${each.key}"
  commit_author       = "Terraform"
  commit_email        = "terraform@localhost"
  overwrite_on_create = true
}

# Add Python files to the feature branch
resource "github_repository_file" "feature_branch" {
  for_each = { for k, v in local.repo_files : k => v if k == "settings.yaml" }

  repository                      = github_repository.workflow_lab.name
  branch                          = var.branch_name
  autocreate_branch               = true
  autocreate_branch_source_branch = github_repository.workflow_lab.default_branch

  file                = each.key
  content             = file(each.value)
  commit_message      = "Add `${each.key}`"
  commit_author       = "Terraform"
  commit_email        = "terraform@localhost"
  overwrite_on_create = true

  # Ensure that this runs after the initial commit to the default branch
  depends_on = [github_repository_file.main]
}
