resource "netcup_dns_record" "a" {
  # Cannot query IP here, since it shows as "", if the machine is started in the plan,
  # producing an inconsistent plan which leads to error.
  # Also problemtic during suspend, because it doesn't realize that the IP will be gone,
  # requiring two apply-runs to actually remove the DNS recond.
  # The fix is to assume that there is only an IP, if the machine is actually running.
  count       = var.dns != null && google_compute_instance.container-host.desired_status == "RUNNING" ? 1 : 0
  zone        = var.dns.zone
  hostname    = var.dns.hostname
  type        = "A"
  destination = local.public_ip
  priority    = 0
}
