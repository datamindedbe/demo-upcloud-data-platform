module "lakekeeper" {
  source = "../../modules/lakekeeper"
  domain = var.hosted_domain
}

module "trino" {
  source = "../../modules/trino"
  domain = var.hosted_domain
}

module "opa" {
  source = "../../modules/opa"
}