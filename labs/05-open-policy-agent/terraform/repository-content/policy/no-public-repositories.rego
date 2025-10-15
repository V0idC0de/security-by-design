package github

import rego.v1

# Define deny rule to identify violations
deny contains msg if {
    resource := input.resource_changes[_]
    resource.type == "github_repository"
    resource.change.after.visibility == "public"

    msg := sprintf("Repository '%s' has public visibility which is not allowed", [resource.address])
}
