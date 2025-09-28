module "traefik" {
  source      = "../../modules/traefik"
  domain      = var.hosted_domain
  admin_email = var.admin_email
}
module "zitadel" {
  source              = "../../modules/zitadel"
  domain              = var.hosted_domain
  zitadel_admin_email = var.admin_email
}