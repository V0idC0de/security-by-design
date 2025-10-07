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
  content = templatefile("${path.module}/ansible-inventory.tpl", {
    ip_address      = local.outputs.public_ip,
    ansible_user    = local.outputs.initial_user,
    priv_path       = local.outputs.ssh.priv_path,
    ssh_config_path = local.outputs.ssh.config_path,
  })
  filename        = local.outputs.inventory_path
  file_permission = "0600"
}
