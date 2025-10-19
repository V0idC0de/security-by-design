# Hosting a Playground

Code involved in hosting an environment in Google Cloud, which allows students to log into a VM on the Internet with pre-defined users,
and are brought directly into a Lab-Environment.

The objective is, to provide Labs of this Repository "as a Service", such that only SSH is necessary to access them.
This provides the barrier to entry and minimized potential errors, related to user-specific environmnets.

## Usage

### Building the Container Host

1. `cd terraform`
2. `terraform init`
3. (Optional) Configure any variables (see `variables.tf`) as required
4. Review the plan of `terraform apply`, then confirm with `yes`

This will create a Project (or reuse an existing Project, if `project_reuse` is `true`),
enable all necessary APIs, create a Service Account, and a Compute Instance.
The Compute Instance will use the Service Account as runtime identity.

The machine is configured with a user for initial access, which is accessible via SSH.
Credentials for this user are also generated alongside the Instance and placed in `ssh`
(which is `../ssh`, relative to `terraform`). A pre-configured `config` file for SSH is also
created, allowing easy login with the alias `lab-host` as destination (e.g. `ssh -F ssh/config lab-host`).

In additon, `ssh/outputs.yaml` is a printed version of `terraform`'s outputs for easy access and reference,
including absolute paths to **SSH Public Key**, **SSH Private Key**, and **SSH Configuration File**.

> [!WARNING]
> Due to how the SSH Private Key is generated and used in Terraform, it has to be stored in the Terraform State.
> Even though the `.key` file produced by Terraform has `0400`-permissions, the Terrafrom State file may be more
> accessible, depending on your configuration. Make sure that **nobody** can access that file or they are able
> to easily log into your VM!

### Initial VM Setup with Ansible

> TODO: More detailled description

1. `apt install pipx`
2. `pipx ensurepath`
3. `pipx install ansible-core==2.19.2`
4. `pipx inject ansible-core passlib==1.7.4`
   1. Additional requirement, which may not be present
5. `ansible-galaxy install -r requirements.yml`
6. `ansible-playbook create-users.yml`
7. `ansible-playbook build-images.yml`
8. 
