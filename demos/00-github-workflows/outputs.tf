output "repo_url" {
  value       = github_repository.workflow_lab.html_url
  description = "Link zum Demo-Repository"
}

output "create_pr_url" {
  value       = "${github_pull_request.create.html_url}/compare/${github_branch_default.workflow_lab.branch}...${github_branch.add_python.branch}"
  description = "Link zum erstellen des Pull-Requests vom Feature Branch"
}
