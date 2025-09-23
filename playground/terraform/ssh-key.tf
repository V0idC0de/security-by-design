locals {
  ssh = {
    pub_path    = abspath("${path.module}/../ssh/${var.machine.username}.pub")
    priv_path   = abspath("${path.module}/../ssh/${var.machine.username}.key")
    config_path = abspath("${path.module}/../ssh/config")
  }
}

resource "tls_private_key" "ssh" {
  algorithm = "ED25519"
}

resource "local_sensitive_file" "ssh_private_key" {
  content         = tls_private_key.ssh.private_key_openssh
  filename        = local.ssh.priv_path
  file_permission = "0600"
}

resource "local_file" "ssh_public_key" {
  content         = tls_private_key.ssh.public_key_openssh
  filename        = local.ssh.pub_path
  file_permission = "0644"
}

resource "local_file" "ssh_config" {
  content         = <<-EOT
Host lab-host
    HostName ${local.outputs.public_ip}
    User ${local.outputs.initial_user}
    IdentityFile ${local.ssh.priv_path}
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
EOT
  filename        = local.ssh.config_path
  file_permission = "0600"
}
