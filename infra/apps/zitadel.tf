module "zitadel_apps" {
  source = "../../modules/zitadel-apps"
  hosted_domain = var.hosted_domain
  organisation_id = var.organisation_id
}