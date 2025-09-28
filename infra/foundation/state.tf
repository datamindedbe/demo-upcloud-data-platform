terraform {
  backend "s3" {
    bucket = var.storage_bucket_name
    key    = "${var.resource_prefix}/terraform.tfstate" #TODO change to dp-stack-foundation.tfstate
    region = var.region

    # We need to skip AWS specific checks and use path style URLs for
    # UpCloud Managed Object Storage.
    skip_requesting_account_id  = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_s3_checksum            = true
    use_path_style              = true

    profile = "upcloud"

    endpoints = {
      s3  = "https://${var.storage_bucket_domain_name}"
      iam = "https://${var.storage_bucket_domain_name}:4443/iam"
      sts = "https://${var.storage_bucket_domain_name}:4443/sts"
    }
  }
  required_version = "1.10.5"
}
