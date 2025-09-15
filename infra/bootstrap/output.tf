output "storage_bucket" {
  value = upcloud_managed_object_storage_bucket.bucket.name
}

output "s3_endpoint_domain" {
  value = tolist(upcloud_managed_object_storage.this.endpoint)[0].domain_name
}

output "s3_user_access_key_id" {
  value = upcloud_managed_object_storage_user_access_key.tf_user.access_key_id
  sensitive = true
}

output "s3_user_access_key_secret" {
  value = upcloud_managed_object_storage_user_access_key.tf_user.secret_access_key
  sensitive = true
}