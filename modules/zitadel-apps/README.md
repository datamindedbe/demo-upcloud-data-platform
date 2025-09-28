<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | 1.10.5 |
| <a name="requirement_kubernetes"></a> [kubernetes](#requirement\_kubernetes) | 2.38.0 |
| <a name="requirement_zitadel"></a> [zitadel](#requirement\_zitadel) | 2.2.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_kubernetes"></a> [kubernetes](#provider\_kubernetes) | 2.38.0 |
| <a name="provider_zitadel"></a> [zitadel](#provider\_zitadel) | 2.2.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [kubernetes_secret.trino_oidc](https://registry.terraform.io/providers/hashicorp/kubernetes/2.38.0/docs/resources/secret) | resource |
| [zitadel_application_oidc.trino](https://registry.terraform.io/providers/zitadel/zitadel/2.2.0/docs/resources/application_oidc) | resource |
| [zitadel_project.trino](https://registry.terraform.io/providers/zitadel/zitadel/2.2.0/docs/resources/project) | resource |
| [zitadel_org.default](https://registry.terraform.io/providers/zitadel/zitadel/2.2.0/docs/data-sources/org) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_hosted_domain"></a> [hosted\_domain](#input\_hosted\_domain) | The hosted domain for your data platform. | `string` | n/a | yes |
| <a name="input_organisation_id"></a> [organisation\_id](#input\_organisation\_id) | The ID of the ZITADEL organisation. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_trino_secret"></a> [trino\_secret](#output\_trino\_secret) | n/a |
<!-- END_TF_DOCS -->