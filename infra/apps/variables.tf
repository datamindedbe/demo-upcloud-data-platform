
variable "hosted_domain" {
  type = string
  description = "The domain name to use for hosting services."
}

variable "organisation_id" {
    type = string
    description = "The ID of the ZITADEL organisation."
}

variable "storage_bucket_name" {
  type = string
  description = "The name of the storage bucket to use for storing terraform state."
}


variable "storage_bucket_domain_name" {
  type = string
  description = "The domain name of the s3 storage bucket endpoint."
}

variable "region" {
  type = string
  default = "europe-1"
  description = "The region to deploy resources in. More details at: https://upcloud.com/docs/products/managed-object-storage/availability/"
}

variable "resource_prefix" {
  type = string
  default = "dp-demo-stack"
  description = "A prefix to use for naming resources."
}
