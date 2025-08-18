resource "github_repository" "workflow_lab" {
  name = var.repository_name

  visibility             = "private" # für Übung im Labor
  auto_init              = true      # Initialisiert mit README
  gitignore_template     = "Python"  # Beispiel, kann angepasst werden!
  delete_branch_on_merge = true

  has_discussions = false
  has_downloads   = false
  has_issues      = false
  has_projects    = false
  has_wiki        = false
}

resource "github_branch" "main" {
  repository = github_repository.workflow_lab.name
  branch     = "main"
}

resource "github_branch_default" "workflow_lab" {
  repository = github_repository.workflow_lab.name
  branch     = github_branch.main.branch
}

# Find all files in repository-content recursively
locals {
  repo_files = {
    for f in fileset("${path.module}/${var.repository_dir}", "**") :
    f => "${path.module}/${var.repository_dir}/${f}"
  }
  repo_files_only_python    = toset([for f, content in local.repo_files : f if endswith(f, ".py")])
  repo_files_without_python = toset([for f, content in local.repo_files : f if !contains(local.repo_files_only_python, f)])
}

resource "github_repository_file" "non_python" {
  for_each       = local.repo_files_without_python
  repository     = github_repository.workflow_lab.name
  file           = each.key
  content        = file(local.repo_files[each.key])
  commit_message = "Add ${each.key}"
}

# Create a feature branch 'add-python' from default branch
resource "github_branch" "add_python" {
  repository    = github_repository.workflow_lab.name
  branch        = "add-python"
  source_branch = github_branch.main.branch
}

# Add Python files to the feature branch
resource "github_repository_file" "python" {
  for_each       = local.repo_files_only_python
  repository     = github_repository.workflow_lab.name
  branch         = github_branch.add_python.branch
  file           = each.key
  content        = file(local.repo_files[each.key])
  commit_message = "Add ${each.key} to add-python branch"
}
