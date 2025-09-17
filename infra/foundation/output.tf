output "db_password" {
  value     = random_password.db_admin_password.result
  sensitive = true
}

output "k8s_cluster_name" {
  value     = upcloud_kubernetes_cluster.this.name
  sensitive = true
}

output "s3_warehouse_info" {
  value     = {
    endpoint  = kubernetes_secret.s3_credentials.data["ENDPOINT"]
    bucket    = kubernetes_secret.s3_credentials.data["BUCKET"]
    region    = kubernetes_secret.s3_credentials.data["REGION"]
    access_key = kubernetes_secret.s3_credentials.data["ACCESS_KEY_ID"]
    secret_key = kubernetes_secret.s3_credentials.data["SECRET_ACCESS_KEY"]
  }
  sensitive = true
}
