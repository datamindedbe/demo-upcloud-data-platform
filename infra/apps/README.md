<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 2.16.1 |
| <a name="requirement_zitadel"></a> [zitadel](#requirement\_zitadel) | 2.2.0 |

## Providers

No providers.

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lakekeeper"></a> [lakekeeper](#module\_lakekeeper) | ../../modules/lakekeeper | n/a |
| <a name="module_opa"></a> [opa](#module\_opa) | ../../modules/opa | n/a |
| <a name="module_trino"></a> [trino](#module\_trino) | ../../modules/trino | n/a |
| <a name="module_zitadel_apps"></a> [zitadel\_apps](#module\_zitadel\_apps) | ../../modules/zitadel-apps | n/a |

## Resources

No resources.

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_hosted_domain"></a> [hosted\_domain](#input\_hosted\_domain) | The domain name to use for hosting services. | `string` | n/a | yes |
| <a name="input_organisation_id"></a> [organisation\_id](#input\_organisation\_id) | The ID of the ZITADEL organisation. | `string` | n/a | yes |
| <a name="input_region"></a> [region](#input\_region) | The region to deploy resources in. More details at: https://upcloud.com/docs/products/managed-object-storage/availability/ | `string` | `"europe-1"` | no |
| <a name="input_resource_prefix"></a> [resource\_prefix](#input\_resource\_prefix) | A prefix to use for naming resources. | `string` | `"dp-demo-stack"` | no |
| <a name="input_storage_bucket_domain_name"></a> [storage\_bucket\_domain\_name](#input\_storage\_bucket\_domain\_name) | The domain name of the s3 storage bucket endpoint. | `string` | n/a | yes |
| <a name="input_storage_bucket_name"></a> [storage\_bucket\_name](#input\_storage\_bucket\_name) | The name of the storage bucket to use for storing terraform state. | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->