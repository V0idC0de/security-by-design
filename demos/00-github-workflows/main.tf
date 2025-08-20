resource "github_repository" "workflow_lab" {
  name = var.repository_name

  visibility             = "public"
  auto_init              = true # Initialisiert mit README, wichtig für Branch Creation
  delete_branch_on_merge = true

  has_discussions = false
  has_downloads   = false
  has_issues      = false
  has_projects    = false
  has_wiki        = false
}

resource "github_branch_default" "default" {
  repository = github_repository.workflow_lab.name
  branch     = "main"
  rename     = true
}

resource "github_branch_protection" "default" {
  repository_id = github_repository.workflow_lab.node_id
  pattern       = github_branch_default.default.branch

  allows_force_pushes = false
  allows_deletions    = false
  enforce_admins      = true

  required_status_checks {
    strict   = true
    contexts = sort(local.ci_jobs)
  }
  depends_on = [github_repository_file.non_python]
}

# Find all files in repository-content recursively
locals {
  repo_files = {
    for f in fileset("${path.module}/${var.repository_dir}", "**") :
    f => "${path.module}/${var.repository_dir}/${f}"
  }
  repo_files_only_python    = toset([for f, content in local.repo_files : f if endswith(f, ".py")])
  repo_files_without_python = toset([for f, content in local.repo_files : f if !contains(local.repo_files_only_python, f)])

  ci_yaml = yamldecode(file("${path.module}/repository-content/.github/workflows/ci.yml"))
  ci_jobs = values(local.ci_yaml.jobs)[*].name
}

resource "github_repository_file" "non_python" {
  for_each            = local.repo_files_without_python
  repository          = github_repository.workflow_lab.name
  branch              = github_branch_default.default.branch
  file                = each.key
  content             = file(local.repo_files[each.key])
  commit_message      = "Add ${each.key}"
  commit_author       = "Terraform"
  commit_email        = "terraform@localhost"
  overwrite_on_create = true

  depends_on = [github_branch_default.default]
}

# Add Python files to the feature branch
resource "github_repository_file" "python" {
  for_each                        = local.repo_files_only_python
  repository                      = github_repository.workflow_lab.name
  branch                          = var.branch_name
  autocreate_branch               = true
  autocreate_branch_source_branch = github_branch_default.default.branch
  file                            = each.key
  content                         = file(local.repo_files[each.key])
  commit_message                  = "Add ${each.key} to add-python branch"
  commit_author                   = "Terraform"
  commit_email                    = "terraform@localhost"
  overwrite_on_create             = true

  depends_on = [github_repository_file.non_python]
}
