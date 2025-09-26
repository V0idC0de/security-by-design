## Ansible Playbook

This playbook connects to a remote Ubuntu machine, installs Git and Docker, creates users, and configures their `sudoers` files.

## Input Variables

| Variable         | Description                                                        | Required | Default Value | Used By Playbooks                        |
|------------------|--------------------------------------------------------------------|----------|--------------|------------------------------------------|
| `lab_users`      | List of usernames for lab participants.                            | Yes      | `[]`         | create-users, lab-containers-up, lab-containers-down |
| `lab_dir`        | Name or part of the lab directory to select the Docker image.      | Yes      | (none)       | lab-containers-up                        |
| `recreate`       | Whether to recreate (remove and start) existing lab containers.    | No       | `false`      | lab-containers-up                        |
| `reset_password` | Whether to reset passwords for lab users to the configured default.| No       | `false`      | create-users                             |
