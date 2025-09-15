variable "k8s_network_range" {
  default = "10.10.0.0/22"
  description = "CIDR range used by the cluster SDN network."
  type = string
}

variable "k8s_version" {
  default = "1.32"
  description = "The kubernetes version to use."
  type = string
}

variable "storage_bucket_name" {
    type = string
    description = "The name of the storage bucket to use for storing terraform state."
}

variable "hosted_domain" {
    type = string
    description = "The domain name to use for hosting services."
}

variable "admin_email" {
    type = string
    description = "The email address to use for the initial admin user in Zitadel."
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

variable "db_plan" {
    type = string
    default = "1x2xCPU-4GB-50GB"
    description = "The database plan to use for the managed database instance. More details at: https://upcloud.com/docs/products/managed-postgresql/configurations/"
}

variable "db_allow_public_access" {
    type = bool
    default = false
    description = "Whether to allow public access to the database instance. Not recommended for production."
}

variable "k8s_default_node_count" {
  default = 3
  type = number
  description = "The number of static nodes to create in the kubernetes worker node group."
}

variable "k8s_default_node_type" {
    type = string
    default = "4xCPU-8GB"
    description = "The node plan to use for the kubernetes worker nodes."
}

variable "resource_prefix" {
    type = string
    default = "dp-demo-stack"
    description = "A prefix to use for naming resources."
}