terraform {
  required_providers {
    upcloud = {
      source  = "upcloudltd/upcloud"
      version = "5.25.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
  required_version = "1.10.5"
}

provider "upcloud" {
} # We do not set the UPCLOUD_USERNAME and UPCLOUD_PASSWORD explicitly here, but rather look for them in your environment variables.
