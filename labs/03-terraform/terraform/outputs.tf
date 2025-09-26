
output "html_urls" {
  description = "Links zu erstellen Repositories"
  value = {
    for repo in github_repository.lab_repo :
    repo.name => repo.html_url
  }
}

output "ssh_urls" {
  description = "SSH-URLs der Repositories"
  value = {
    for repo in github_repository.lab_repo :
    repo.name => repo.ssh_clone_url
  }
}
