provider "zitadel" {
  domain           = "zitadel.${var.hosted_domain}"
  jwt_profile_file = "token.json"
}

terraform {
  required_providers {
    zitadel = {
      source  = "zitadel/zitadel"
      version = "2.2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.38.0"
    }
  }
}

provider "kubernetes" {
  config_path = "../.kubeconfig.yml"
}

provider "helm" {
  kubernetes {
    config_path = "../.kubeconfig.yml"
  }
}
