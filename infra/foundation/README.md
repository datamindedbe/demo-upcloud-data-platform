<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | 1.10.5 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 2.16.1 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | 2.38.0 |
| <a name="requirement_local"></a> [local](#requirement\_local) | 2.5.3 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.6.3 |
| <a name="requirement_upcloud"></a> [upcloud](#requirement\_upcloud) | 5.25.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | 2.38.0 |
| <a name="provider_local"></a> [local](#provider\_local) | 2.5.3 |
| <a name="provider_random"></a> [random](#provider\_random) | 3.6.3 |
| <a name="provider_upcloud"></a> [upcloud](#provider\_upcloud) | 5.25.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_traefik"></a> [traefik](#module\_traefik) | ../../modules/traefik | n/a |
| <a name="module_zitadel"></a> [zitadel](#module\_zitadel) | ../../modules/zitadel | n/a |

## Resources

| Name | Type |
|------|------|
| [kubernetes_namespace.opa](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/namespace) | resource |
| [kubernetes_namespace.services](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/namespace) | resource |
| [kubernetes_namespace.traefik](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/namespace) | resource |
| [kubernetes_secret.lakekeeper_db](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/secret) | resource |
| [kubernetes_secret.pg_credentials](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/secret) | resource |
| [kubernetes_secret.s3_credentials](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/secret) | resource |
| [kubernetes_secret.zitadel_db](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/secret) | resource |
| [local_sensitive_file.kubeconfig](https://registry.terraform.io/providers/hashicorp/local/2.5.3/docs/resources/sensitive_file) | resource |
| [random_password.db_admin_password](https://registry.terraform.io/providers/hashicorp/random/3.6.3/docs/resources/password) | resource |
| [random_string.random](https://registry.terraform.io/providers/hashicorp/random/3.6.3/docs/resources/string) | resource |
| [upcloud_gateway.gw](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/gateway) | resource |
| [upcloud_kubernetes_cluster.this](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/kubernetes_cluster) | resource |
| [upcloud_kubernetes_node_group.default_group](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/kubernetes_node_group) | resource |
| [upcloud_managed_database_logical_database.lakekeeper_db](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_database_logical_database) | resource |
| [upcloud_managed_database_postgresql.db](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_database_postgresql) | resource |
| [upcloud_managed_object_storage.dp-stack-data](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_object_storage) | resource |
| [upcloud_managed_object_storage_bucket.bucket](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_object_storage_bucket) | resource |
| [upcloud_managed_object_storage_user.storage_user](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_object_storage_user) | resource |
| [upcloud_managed_object_storage_user_access_key.storage_key](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_object_storage_user_access_key) | resource |
| [upcloud_managed_object_storage_user_policy.this](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/managed_object_storage_user_policy) | resource |
| [upcloud_network.k8s_private_node_network](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/network) | resource |
| [upcloud_router.router](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/resources/router) | resource |
| [upcloud_kubernetes_cluster.this](https://registry.terraform.io/providers/UpCloudLtd/upcloud/5.25.0/docs/data-sources/kubernetes_cluster) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_admin_email"></a> [admin\_email](#input\_admin\_email) | The email address to use for the initial admin user in Zitadel. | `string` | n/a | yes |
| <a name="input_db_allow_public_access"></a> [db\_allow\_public\_access](#input\_db\_allow\_public\_access) | Whether to allow public access to the database instance. Not recommended for production. | `bool` | `false` | no |
| <a name="input_db_plan"></a> [db\_plan](#input\_db\_plan) | The database plan to use for the managed database instance. More details at: https://upcloud.com/docs/products/managed-postgresql/configurations/ | `string` | `"1x2xCPU-4GB-50GB"` | no |
| <a name="input_hosted_domain"></a> [hosted\_domain](#input\_hosted\_domain) | The domain name to use for hosting services. | `string` | n/a | yes |
| <a name="input_k8s_default_node_count"></a> [k8s\_default\_node\_count](#input\_k8s\_default\_node\_count) | The number of static nodes to create in the kubernetes worker node group. | `number` | `2` | no |
| <a name="input_k8s_default_node_type"></a> [k8s\_default\_node\_type](#input\_k8s\_default\_node\_type) | The node plan to use for the kubernetes worker nodes. | `string` | `"4xCPU-8GB"` | no |
| <a name="input_k8s_network_range"></a> [k8s\_network\_range](#input\_k8s\_network\_range) | CIDR range used by the cluster SDN network. | `string` | `"10.10.0.0/22"` | no |
| <a name="input_k8s_version"></a> [k8s\_version](#input\_k8s\_version) | The kubernetes version to use. | `string` | `"1.32"` | no |
| <a name="input_region"></a> [region](#input\_region) | The region to deploy resources in. More details at: https://upcloud.com/docs/products/managed-object-storage/availability/ | `string` | `"europe-1"` | no |
| <a name="input_resource_prefix"></a> [resource\_prefix](#input\_resource\_prefix) | A prefix to use for naming resources. | `string` | `"dp-demo-stack"` | no |
| <a name="input_storage_bucket_domain_name"></a> [storage\_bucket\_domain\_name](#input\_storage\_bucket\_domain\_name) | The domain name of the s3 storage bucket endpoint. | `string` | n/a | yes |
| <a name="input_storage_bucket_name"></a> [storage\_bucket\_name](#input\_storage\_bucket\_name) | The name of the storage bucket to use for storing terraform state. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_db_password"></a> [db\_password](#output\_db\_password) | n/a |
| <a name="output_k8s_cluster_name"></a> [k8s\_cluster\_name](#output\_k8s\_cluster\_name) | n/a |
| <a name="output_s3_warehouse_info"></a> [s3\_warehouse\_info](#output\_s3\_warehouse\_info) | n/a |
<!-- END_TF_DOCS -->