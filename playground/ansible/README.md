# Ansible Playbook

This playbook connects to a remote Ubuntu machine, installs Git and Docker, creates users, and configures their `sudoers` files.

## Input Variables

| Variable         | Description                                                        | Required | Default Value | Used By Playbooks                        |
|------------------|--------------------------------------------------------------------|----------|--------------|------------------------------------------|
| `lab_users`      | List of usernames for lab participants.                            | Yes      | `[]`         | create-users, lab-containers-up, lab-containers-down |
| `lab_dir`        | Name or part of the lab directory to select the Docker image.      | Yes      | (none)       | lab-containers-up                        |
| `recreate`       | Whether to recreate (remove and start) existing lab containers.    | No       | `false`      | lab-containers-up                        |
| `reset_password` | Whether to reset passwords for lab users to the configured default.| No       | `false`      | create-users                             |

## Usage

### Quick Reference

#### Setup

All actions required to setup the environment, ready to use for Lab exercises.

```bash
apt install pipx
pipx ensurepath
pipx install ansible-core==2.19.2
pipx inject ansible-core passlib==1.7.4
ansible-galaxy install -r requirements.yml
ansible-playbook create-users.yml
ansible-playbook build-images.yml
```

#### Create Lab Containers

```bash
ansible-playbook lab-containers-down.yml 
ansible-playbook lab-containers-up.yml
```

#### [Stop Lab Containers](#stopdisable-a-lab)

#### [Reset a User Password](#reset-user-passwords)

### Dependencies

1. Install `pipx`
   1. `apt install pipx`
2. Ensure, that things installed by `pipx` are on the `$PATH` variable
   1. `pipx ensurepath`
3. Install **Ansible** and inject the `passlib` as a requirement
   1. `pipx install ansible-core==2.19.2`
   2. `pipx inject ansible-core passlib==1.7.4`
4. Install dependencies from **Ansible Galaxy**
   1. `ansible-galaxy install -r requirements.yml`

### Run Playbooks on Lab Host

1. **Terraform** (see [terraform](../terraform/)) should have written a file called `inventory` into the `ansible` directory
   1. If that is not the case, go back to `../terraform` and run `terraform apply`
2. Fill out `vars/settings.sample.yaml`, then remove the `.sample` from the filename, so it's `settings.yaml`.
3. While in the `ansible` directory, execute `ansible-playbook <playbook-file>.yml`
   1. Append `-e VAR_NAME=VALUE` for any explicit extra settings

### Create Users

A list of usernames should be provided as variable (for example via `vars/settings.yaml`). They must be valid Linux usernames.
Then run the corresponding playbook, which will accomplish the following:

1. Create user, if not already present
2. Set password for user, if newly created or forced by `reset_password=true`
3. (If password was set/modified) Expire the password
4. (If user was changed) Set the users sshd configuration to a command, that displays a message and quits immediately, blocking access

```bash
ansible-playbook create-users.yml
```

> [!NOTE]
> This playbook will create the users and set an initial password, which is equal to their username.
> That password will be expired immediately, forcing a change on first login.
> If the user changes the password, the Playbook will **not** reset it, unless `reset_password` is set to `true`.
> Instead of `create-users.yml`, use `reset-password.yml` for this, as it is intended to target single users.

#### Reset User Passwords

This Playbook will ask for the username. If it exists, its password will be set to its username.
If it doesn't exist, the user will be created. However, this is not the preferred method to create users.
If that happens, add the user to `lab_users` in `vars/settings.yaml`, then run [Create Users](#create-users) again.

```bash
ansible-playbook reset-password.yml
```

### Lab Operations

#### Build Images

It is beneficial to build all Images in advance, so they are ready to use.
Playbooks might fail, if the images are not available locally.

```bash
ansible-playbook build-images.yml
```

#### Start/Enable a Lab

Run [Stop a Lab](#stopdisable-a-lab) to ensure no competing Containers are currently up.
This is better in terms of resources and also configuration, since there can be only one
`sshd` and `sudoers` configuration allowing Lab access for a given user.

The Playbook will ask for the name of a Container Image (= lab folder name) or parts of it.
As long as only one image matches the given phrase, it will auto-select it. If there are 0 or more than 1,
an error is returned.

One Container will be created per `lab_user`, configuring `sshd` so the user is connected to a shell in that
Container, should they connect via `ssh`.

```bash
ansible-playbook lab-containers-up.yml
```

#### Stop/Disable a Lab

This Playbook will stop all Containers, whose name starts with `lab-`, regardless of user or active sessions.
This terminates any active sessions forcefully.
It will also set the `sshd` configuration, so that the user cannot login anymore.
Setting `delete_containers=true` will remove the Containers after stopping them.

In addition, `sshd` will be reconfigured, such that the user's access is blocked again, only displaying a message on login.

```bash
ansible-playbook lab-containers-down.yml
# To remove Containers
ansible-playbook lab-containers-down.yml -e delete_containers=true
```
