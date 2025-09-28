# Customized OPA Module

In order to configure OPA with Lakekeeper, we tweaked the policies that are provided by default in the [Lakekeeper]().
For this demo setup we allow all actions, but in a production setup you should restrict access as much as possible.

In order to restrict the access, you need to do the following:

- Enable authentication in Trino and Lakekeeper, this is done by setting up Zitadel as an OIDC provider.
- Set default allow to false in the `modules/opa/policies/trino/main.rego` file.
- Modify the `modules/opa/policies/lakekeeper/*.rego` files to use authentication and check permission in Lakekeeper.

## Customizing the image

Run the following commands to build and push the customized OPA image:

```bash
docker build -t <your-docker-repo>/data-stack-opa:latest -f ./
docker push <your-docker-repo>/data-stack-opa:latest
```

Make sure to update the image in `modules/opa/main.tf` accordingly.
<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | 1.10.5 |
| <a name="requirement_helm"></a> [helm](#requirement\_helm) | 2.16.1 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_helm"></a> [helm](#provider\_helm) | 2.16.1 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [helm_release.opa](https://registry.terraform.io/providers/hashicorp/helm/2.16.1/docs/resources/release) | resource |

## Inputs

No inputs.

## Outputs

No outputs.
<!-- END_TF_DOCS -->