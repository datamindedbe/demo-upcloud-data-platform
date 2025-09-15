resource "upcloud_kubernetes_cluster" "this" {
  name                    = "${var.resource_prefix}-k8s-cluster"
  network                 = upcloud_network.k8s_private_node_network.id
  control_plane_ip_filter = ["0.0.0.0/0"]
  zone                    = local.zone
  private_node_groups     = true
  version = var.k8s_version
  storage_encryption = "data-at-rest"
  upgrade_strategy_type = "manual"

  labels = {
    managed_by = "terraform"
    project = var.resource_prefix
  }
}


resource "upcloud_kubernetes_node_group" "default_group" {
  name = "${var.resource_prefix}-k8s-default-node-group"
  cluster    = upcloud_kubernetes_cluster.this.id
  node_count = var.k8s_default_node_count
  plan = var.k8s_default_node_type
  anti_affinity = false

  labels = {
    managed_by = "terraform"
    project = var.resource_prefix
  }
  ssh_keys = []
}

data "upcloud_kubernetes_cluster" "this" {
  id = upcloud_kubernetes_cluster.this.id
}

resource "local_sensitive_file" "kubeconfig" {
  filename        = "${path.module}/../.kubeconfig.yml"
  content         = data.upcloud_kubernetes_cluster.this.kubeconfig
  file_permission = "0600"
}

resource "kubernetes_namespace" "services" {
  metadata {
    name = "services"
  }
}
