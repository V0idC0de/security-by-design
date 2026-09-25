resource "netcup_dns_record" "a" {
  count       = var.dns != null ? 1 : 0
  zone        = var.dns.zone
  hostname    = var.dns.hostname
  type        = "A"
  destination = local.public_ip
  priority    = 0
}
