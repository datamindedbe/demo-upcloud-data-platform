# Bootstrapping

This directory is used to bootstrap storage bucket on UpCloud, which will be used to store the terraform state.

## Steps

- Make sure your UpCloud credentials are available as environment variables. You can source the .env.template after updating the username or password or you can run:
  - export UPCLOUD_USERNAME="your_upcloud_username" 
  - export UPCLOUD_PASSWORD="your_upcloud_password"
- run `tofu init` to initialize the terraform backend
- run `tofu apply` to create the storage bucket

<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | 1.10.5 |
| <a name="requirement_random"></a> [random](#requirement\_random) | 3.6.3 |
| <a name="requirement_upcloud"></a> [upcloud](#requirement\_upcloud) | 5.25.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_random"></a> [random](#provider\_random) | 3.6.3 |
| <a name="provider_upcloud"></a> [upcloud](#provider\_upcloud) | 5.25.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [random_string.random-suffix](https://registry.terraform.io/providers/hashicorp/random/3.6.3/docs/resources/string) | resource |
| [upcloud_managed_object_storage.this](https://registry.terraform.io/providers/upcloudltd/upcloud/5.25.0/docs/resources/managed_object_storage) | resource |
| [upcloud_managed_object_storage_bucket.bucket](https://registry.terraform.io/providers/upcloudltd/upcloud/5.25.0/docs/resources/managed_object_storage_bucket) | resource |
| [upcloud_managed_object_storage_user.tf_user](https://registry.terraform.io/providers/upcloudltd/upcloud/5.25.0/docs/resources/managed_object_storage_user) | resource |
| [upcloud_managed_object_storage_user_access_key.tf_user](https://registry.terraform.io/providers/upcloudltd/upcloud/5.25.0/docs/resources/managed_object_storage_user_access_key) | resource |
| [upcloud_managed_object_storage_user_policy.this](https://registry.terraform.io/providers/upcloudltd/upcloud/5.25.0/docs/resources/managed_object_storage_user_policy) | resource |

## Inputs

No inputs.

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_s3_endpoint_domain"></a> [s3\_endpoint\_domain](#output\_s3\_endpoint\_domain) | n/a |
| <a name="output_s3_user_access_key_id"></a> [s3\_user\_access\_key\_id](#output\_s3\_user\_access\_key\_id) | n/a |
| <a name="output_s3_user_access_key_secret"></a> [s3\_user\_access\_key\_secret](#output\_s3\_user\_access\_key\_secret) | n/a |
| <a name="output_storage_bucket"></a> [storage\_bucket](#output\_storage\_bucket) | n/a |
<!-- END_TF_DOCS -->