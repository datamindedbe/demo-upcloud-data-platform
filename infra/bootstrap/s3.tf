resource "random_string" "random-suffix" {
  length  = 6
  special = false
  upper   = false
}

resource "upcloud_managed_object_storage" "this" {
  name              = "dp-stack-tf-state-${random_string.random-suffix.result}"
  region            = "europe-1" # Location is in Finland, alternatives are: EUROPE-2 (Germany), US-1 (USA), EUROPE-3 (Sweden)
  configured_status = "started"

  labels = {
    managed_by = "terraform"
  }

  network {
    family = "IPv4"
    name   = "my-public-network"
    type   = "public"
  }
}

resource "upcloud_managed_object_storage_bucket" "bucket" {
  service_uuid = upcloud_managed_object_storage.this.id
  name         = "dp-stack-state-bucket"
}

resource "upcloud_managed_object_storage_user" "tf_user" {
  username     = "tf-state-user"
  service_uuid = upcloud_managed_object_storage.this.id
}

resource "upcloud_managed_object_storage_user_access_key" "tf_user" {
  username     = upcloud_managed_object_storage_user.tf_user.username
  service_uuid = upcloud_managed_object_storage.this.id
  status       = "Active"
}

resource "upcloud_managed_object_storage_user_policy" "this" {
  username     = upcloud_managed_object_storage_user.tf_user.username
  service_uuid = upcloud_managed_object_storage.this.id
  name         = "ECSS3FullAccess"
}