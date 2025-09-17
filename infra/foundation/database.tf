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
resource "upcloud_managed_database_logical_database" "lakekeeper_db" {
  service = upcloud_managed_database_postgresql.db.id
  name    = "lakekeeper"
}

resource "kubernetes_secret" "lakekeeper_db" {
  metadata {
    name = "lakekeeper-custom-secrets"
    namespace = "services"
  }
  data = {
    ICEBERG_REST__PG_HOST_R=upcloud_managed_database_postgresql.db.service_host
    ICEBERG_REST__PG_HOST_W=upcloud_managed_database_postgresql.db.service_host
    ICEBERG_REST__PG_PORT=upcloud_managed_database_postgresql.db.service_port
    ICEBERG_REST__PG_PASSWORD=upcloud_managed_database_postgresql.db.service_password
    ICEBERG_REST__PG_DATABASE=upcloud_managed_database_logical_database.lakekeeper_db.name
    ICEBERG_REST__PG_USER=upcloud_managed_database_postgresql.db.service_username
    ICEBERG_REST__SECRETS_BACKEND="Postgres"
    LAKEKEEPER__AUTHZ_BACKEND="allowall"
  }
  depends_on = [kubernetes_namespace.services]
}

