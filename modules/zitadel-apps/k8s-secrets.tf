
resource "kubernetes_secret" "trino_oidc" {
  metadata {
    name      = "trino-oidc"
    namespace = "services"
  }

  data = {
    CLIENT_ID     = zitadel_application_oidc.trino.client_id
    CLIENT_SECRET = zitadel_application_oidc.trino.client_secret

  }

  type = "Opaque"
}

resource "kubernetes_secret" "trino_lakekeeper_credentials" {
  metadata {
    name      = "trino-lakekeeper-credentials"
    namespace = "services"
  }

  data = {
    CLIENT_ID     = zitadel_machine_user.trino-opa.client_id
    CLIENT_SECRET = zitadel_machine_user.trino-opa.client_secret
  }

  type = "Opaque"
}

resource "kubernetes_secret" "opa_lakekeeper_oidc" {
  metadata {
    name      = "opa-lakekeeper-credentials"
    namespace = "opa"
  }

  data = {
    CLIENT_ID     = zitadel_machine_user.trino-opa.client_id
    CLIENT_SECRET = zitadel_machine_user.trino-opa.client_secret
  }

  type = "Opaque"
}


resource "kubernetes_secret" "lakekeeper_ui_oidc" {
  metadata {
    name      = "lakekeeper-ui-oidc"
    namespace = "services"
  }

  data = {
    CLIENT_ID     = zitadel_application_oidc.lakekeeper_ui.client_id
  }

  type = "Opaque"
}