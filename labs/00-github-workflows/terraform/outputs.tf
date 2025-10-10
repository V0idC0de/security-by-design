output "repo_url" {
  value       = github_repository.workflow_lab.html_url
  description = "Link zum Demo-Repository"
}

output "create_pr_url" {
  value       = "${github_repository.workflow_lab.html_url}/compare/${github_branch_default.default.branch}...${var.branch_name}"
  description = "Link zum erstellen des Pull-Requests vom Feature Branch"
}

output "repo" {
  value = github_repository.workflow_lab.full_name
}

output "repo-name" {
  value = github_repository.workflow_lab.name
}