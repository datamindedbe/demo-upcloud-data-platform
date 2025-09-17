resource "upcloud_managed_object_storage" "dp-stack-data" {
  name              = "${var.resource_prefix}-${random_string.random.result}"
  region            = var.region
  configured_status = "started"

  network {
    family = "IPv4"
    name   = "my-public-network"
    type   = "public"
  }

    labels = {
        managed_by = "terraform"
        project    = var.resource_prefix
    }
}

resource "upcloud_managed_object_storage_bucket" "bucket" {
  service_uuid = upcloud_managed_object_storage.dp-stack-data.id
  name         = "dp-data-bucket"
}

resource "random_string" "random" {
  length  = 16
  special = false
  upper   = false
}


resource "kubernetes_secret" "s3_credentials" {
  metadata {
    name      = "s3-credentials"
    namespace = kubernetes_namespace.services.metadata[0].name
  }

  data = {
    ACCESS_KEY_ID     = upcloud_managed_object_storage_user_access_key.storage_key.access_key_id
    SECRET_ACCESS_KEY = upcloud_managed_object_storage_user_access_key.storage_key.secret_access_key
    ENDPOINT          = tolist(upcloud_managed_object_storage.dp-stack-data.endpoint)[0].domain_name
    BUCKET            = upcloud_managed_object_storage_bucket.bucket.name
    REGION            = var.region
  }

  type = "Opaque"
}

resource "upcloud_managed_object_storage_user" "storage_user" {
  username     = "${var.resource_prefix}-data-user"
  service_uuid = upcloud_managed_object_storage.dp-stack-data.id
}

resource "upcloud_managed_object_storage_user_access_key" "storage_key" {
  username     = upcloud_managed_object_storage_user.storage_user.username
  service_uuid = upcloud_managed_object_storage.dp-stack-data.id
  status       = "Active"
}


resource "upcloud_managed_object_storage_user_policy" "this" {
  username     = upcloud_managed_object_storage_user.storage_user.username
  service_uuid = upcloud_managed_object_storage.dp-stack-data.id
  name         = "ECSS3FullAccess"
}
