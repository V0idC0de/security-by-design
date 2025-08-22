data "github_user" "me" {
  # Empty string gets the authenticated user dynamically
  username = ""
}

resource "github_repository" "lab_repo" {
  for_each = toset(var.repository_names)

  name        = each.value
  description = "Created via Terraform by ${data.github_user.me.login} (${data.github_user.me.id})"

  visibility = "public"
  auto_init  = true # Initialisiert mit README, wichtig für Branch Creation

  has_discussions = false
  has_downloads   = false
  has_issues      = false
  has_projects    = false
  has_wiki        = false
}

resource "github_branch_default" "default" {
  for_each = toset(var.repository_names)

  repository = github_repository.lab_repo[each.value].name
  branch     = var.default_branch
  rename     = true
}

locals {
  # Generiere eine Map mit einem Eintrag für jedes Paar
  # von Datei und Repository, sodass alle zu platzierenden
  # Dateien gelistet sind, um sie dann auf einmal zu erstellen.

  # type: [ [x1, y1], [x1, y2], ..., [xN, yN] ]
  repo_file_pairs = setproduct(
    toset(var.repository_names),
    toset(var.files)
  )

  # type: {
  #   "repo_name1:file_name1" => {
  #     file = file_name1
  #     repo = repo_name1
  #   },
  #   "repo_name1:file_name2" => {
  #     ...
  #   },
  #   ...
  # }
  files_in_repos = {
    for pair in local.repo_file_pairs :
    "${pair[0]}:${pair[1]}" => {
      repo = pair[0]
      file = pair[1]
    }
  }
}

# Benutze hier die erstelle Map mit Einträgen für jede Datei
# in jedem Repository. Nutze das Objekt in `each.value` um
# auf die beiden Werte zuzugreifen.
# Keys für Maps, aus denen via `for_each` Ressourcen werden,
# MÜSSEN Zahlen oder Strings sein und dürfen keine Duplikate enthalten.
resource "github_repository_file" "lab_file" {
  for_each = local.files_in_repos

  repository = github_repository.lab_repo[each.value.repo].name
  branch     = github_branch_default.default[each.value.repo].branch
  file       = each.value.file
  content    = "Copyright by ${data.github_user.me.login}"

  commit_message      = "Add ${each.value.file}"
  commit_author       = "Terraform"
  commit_email        = "terraform@localhost"
  overwrite_on_create = true
}
