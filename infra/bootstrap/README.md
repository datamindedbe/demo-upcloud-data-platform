# Bootstrapping

This directory is used to bootstrap storage bucket on Upcloud, which will be used to store the terraform state.

## Steps

- Make sure your Upcloud credentials are available as environment variables. You can use the .env.template to create a .env file with the credentials.
  - UPCLOUD_USERNAME
  - UPCLOUD_PASSWORD
- run `tofu init` to initialize the terraform backend
- run `tofu apply` to create the storage bucket