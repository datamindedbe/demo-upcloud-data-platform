resource "upcloud_network" "k8s_private_node_network" {
  name = "${var.resource_prefix}-private-node-net"
  zone = local.zone
  ip_network {
    address            = var.k8s_network_range
    dhcp               = true
    family             = "IPv4"
    dhcp_default_route = true
  }
  router = upcloud_router.router.id
}

resource "upcloud_router" "router" {
  name = "${var.resource_prefix}-k8s-router"
  labels = {
    managed_by = "terraform"
    project = var.resource_prefix
  }
}

resource "upcloud_gateway" "gw" {
  name     = "${var.resource_prefix}-nat-gateway"
  zone     = local.zone
  features = ["nat"]

  router {
    id = upcloud_router.router.id
  }

  labels = {
    managed_by = "terraform"
    project = var.resource_prefix
  }
}
