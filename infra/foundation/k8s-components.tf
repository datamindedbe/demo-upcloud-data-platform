module "traefik" {
  source      = "../../modules/traefik"
  domain      = var.hosted_domain
}
module "zitadel" {
  source              = "../../modules/zitadel"
  domain              = var.hosted_domain
  zitadel_admin_email = var.admin_email
}