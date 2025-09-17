output "db_password" {
  value     = random_password.db_admin_password.result
  sensitive = true
}

output "k8s_cluster_name" {
  value     = upcloud_kubernetes_cluster.this.name
  sensitive = true
}