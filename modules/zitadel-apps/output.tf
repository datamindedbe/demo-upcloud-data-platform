output "trino_secret" {
  sensitive = true
  value = {
    CLIENT_ID     = zitadel_application_oidc.trino.client_id
    CLIENT_SECRET = zitadel_application_oidc.trino.client_secret
  }
}