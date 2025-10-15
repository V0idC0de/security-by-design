package github

import rego.v1

# This policy denies Terraform plans that include repositories with "coffee" in their name
deny contains msg if {
    # Get all resources of type github_repository
    resource := input.resource_changes[_]
    resource.type == "github_repository"

    # Check if "coffee" is in the repository name (case insensitive)
    contains(lower(resource.change.after.name), "coffee")

    # Create denial message
    msg := sprintf(
        "Repository '%s' contains the word 'coffee' which is not allowed",
        [resource.change.after.name]
    )
}
