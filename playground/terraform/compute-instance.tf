resource "google_service_account" "container-host" {
  account_id   = "container-host"
  display_name = "Compute Instance Account for Container Host Machine"
  project      = local.project.project_id
}

data "google_compute_image" "ubuntu" {
  family  = "ubuntu-minimal-2404-lts-amd64"
  project = "ubuntu-os-cloud"
}

resource "google_compute_instance" "container-host" {
  name        = "container-host"
  description = "Host Machine for Lab Containers"

  project = local.project.project_id
  zone    = "${var.region}-a"
  service_account {
    email  = google_service_account.container-host.email
    scopes = ["cloud-platform"]
  }
  deletion_protection       = false
  allow_stopping_for_update = true
  desired_status            = upper(var.machine_state)

  machine_type = var.machine.type
  # FQDN hostname - may require DNS to be set up first?
  # Check automatic instance names first
  # hostname = 
  boot_disk {
    initialize_params {
      image = data.google_compute_image.ubuntu.self_link
      size  = var.machine.disk_size_gb
      type  = var.machine.disk_type
    }
    auto_delete = var.machine.disk_auto_delete
  }

  ## Local SSD disk
  # scratch_disk {
  #  interface = "NVME"
  # }
  network_interface {
    # TODO
    ### Private IP,will be chosen automatically, if unset
    # network_ip = "1.2.3.4"
    network    = "default"
    stack_type = "IPV4_ONLY"
    access_config {
      network_tier = "STANDARD"
    }
  }

  metadata = {
    # "startup-script" = <<-EOF
    #  #!/bin/bash
    #  EOF

    # https://cloud.google.com/compute/docs/metadata/predefined-metadata-keys#project-attributes-metadata
    "ssh-keys" = "${var.machine.username}:${tls_private_key.ssh.public_key_openssh}"
  }

  # Prevent machine from being recreated if only the image changes
  # TODO: Setup proper boot disk management, so this is more interchangeable
  lifecycle {
    ignore_changes = [boot_disk[0].initialize_params[0].image]
  }
}
