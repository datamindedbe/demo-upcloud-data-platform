resource "upcloud_managed_database_postgresql" "db" {
  name  = "${var.resource_prefix}-postgres"
  plan  = var.db_plan
  title = "postgres"
  zone  = local.zone
  properties {
    public_access  = true
    timezone       = "Europe/Helsinki"
    admin_username = "admin"
    admin_password = random_password.db_admin_password.result
    version = "17"
  }
  maintenance_window_dow = "monday"
  maintenance_window_time = "20:00:00"

  labels = {
    managed_by = "terraform"
    project = var.resource_prefix
  }
}

resource "random_password" "db_admin_password" {
  length  = 16
  special = false
}

resource "kubernetes_secret" "pg_credentials" {
  metadata {
    name      = "pg-credentials"
    namespace = kubernetes_namespace.services.metadata[0].name
  }

  data = {
    USERNAME = upcloud_managed_database_postgresql.db.service_username
    PASSWORD = upcloud_managed_database_postgresql.db.service_password
    HOST     = upcloud_managed_database_postgresql.db.service_host
    PORT     = upcloud_managed_database_postgresql.db.service_port
    URI      = upcloud_managed_database_postgresql.db.service_uri
  }

  type = "Opaque"
}

# TODO seems that you cannot retrieve this automatically, only using the UI? Disabling for now.
# resource "kubernetes_secret" "db_certficate" {
#   metadata {
#     name      = "pg-certificate"
#     namespace = kubernetes_namespace.services.metadata[0].name
#   }
#
#   data = {
#     "ca.crt" = upcloud_managed_database_postgresql.db.cercertificate
#   }
#   type = "Opaque"
# }

resource "kubernetes_secret" "zitadel_db" {
  metadata {
    name = "zitadel-credentials"
    namespace = kubernetes_namespace.services.metadata[0].name
  }
  data = { "config.yaml": <<EOF
    Database:
      Postgres:
        Host: ${upcloud_managed_database_postgresql.db.service_host}
        Port: ${upcloud_managed_database_postgresql.db.service_port}
        Database: zitadel
        User:
          Username: ${upcloud_managed_database_postgresql.db.service_username}
          Password: ${upcloud_managed_database_postgresql.db.service_password}
          SSL:
            Mode: prefer
        Admin:
          Username: ${upcloud_managed_database_postgresql.db.service_username}
          Password: ${upcloud_managed_database_postgresql.db.service_password}
          ExistingDatabase: defaultdb
          SSL:
            Mode: prefer
  EOF
  }
  type = "Opaque"
}
