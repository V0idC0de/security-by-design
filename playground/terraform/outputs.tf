locals {
  outputs = {
    public_ip      = google_compute_instance.container-host.network_interface[0].access_config[0].nat_ip
    initial_user   = var.machine.username
    inventory_path = abspath("${path.module}/../ansible/inventory")
    ssh            = { for k, v in local.ssh : k => abspath(v) }
  }
}

output "public_ip" {
  description = "Public IP address of the VM."
  value       = local.outputs.public_ip
}

output "initial_user" {
  description = "Username for inital access to the VM (has sudo privileges)."
  value       = local.outputs.initial_user
}

output "ssh" {
  description = "Absolute paths to files relevant to SSH access."
  value       = local.outputs.ssh
}

resource "local_file" "outputs_yaml" {
  content         = yamlencode(local.outputs)
  filename        = "${path.module}/../ssh/outputs.yaml"
  file_permission = "0600"
}

resource "local_file" "ansible_inventory" {
  content = join(" ", [
    local.outputs.public_ip,
    "ansible_user=${local.outputs.initial_user}",
    "ansible_ssh_private_key_file=${local.outputs.ssh.priv_path}",
    "ansible_ssh_common_args='-F ${local.ssh.config_path} -o StrictHostKeyChecking=no'",
  ])
  filename        = local.outputs.inventory_path
  file_permission = "0600"
}
