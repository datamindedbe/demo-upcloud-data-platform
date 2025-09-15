terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# terraform {
#   required_providers {
#     upcloud = {
#       source  = "UpCloudLtd/upcloud"
#       version = "5.22.1"
#     }
#   }
# }

# provider "upcloud" {
#   username = var.upcloud_username
#   password = var.upcloud_password
# }
