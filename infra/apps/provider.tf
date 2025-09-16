provider "zitadel" {
  domain           = "zitadel.${var.hosted_domain}"
  jwt_profile_json = file("${path.module}/token.json")
}

terraform {
  required_providers {
    zitadel = {
      source  = "zitadel/zitadel"
      version = "2.2.0"
    }
  }
}

provider "kubernetes" {
  config_path = "../.kubeconfig.yml"
}
