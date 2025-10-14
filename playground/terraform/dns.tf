# Not exactly clean, since this will run on every `play` already.
# However, this is a clean way to keep the DNS settings in Terraform.
data "http" "duckdns-update" {
  count  = var.dns_name != null && var.duckdns_token != null && local.public_ip != null ? 1 : 0
  url    = "https://www.duckdns.org/update?domains=${var.dns_name}&token=${var.duckdns_token}&ip=${local.public_ip}"
  method = "GET"
}
