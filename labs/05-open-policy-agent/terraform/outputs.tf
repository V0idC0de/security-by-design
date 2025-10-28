output "repo_url" {
  value       = github_repository.workflow_lab.html_url
  description = "Link zum Demo-Repository"
}

output "create_pr_url" {
  value       = "${github_repository.workflow_lab.html_url}/compare/${github_repository.workflow_lab.default_branch}...${var.branch_name}"
  description = "Link zum erstellen des Pull-Requests vom Feature Branch"
}
