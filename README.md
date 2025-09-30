<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![APACHE License][license-shield]][license-url]

# UpCloud data platform

This repo contains the code for building an open-source data platform on [UpCloud](https://upcloud.com/).

The data platform currently includes the following components:

- **[Trino](https://trino.io/)**: A distributed SQL engine for interactive queries across large and small datasets
  It allows us to build a data warehouse on UpCloud without depending on a managed service.
- **[Lakekeeper](https://docs.lakekeeper.io/)**: The production-ready metadata catalog for Iceberg tables, tightly integrated with Trino and OPA.
- **[Open policy agent (OPA)]()**: A general-purpose policy engine used here to enforce fine-grained data access control.
- **[Traefik](https://traefik.io/)**: A reverse proxy and ingress controller that manages SSL termination and routes traffic to the different services of our data platform.
- **[Zitadel](https://zitadel.com/)**: An identity and access management platform that handles user and application authentication, with support for integration into your company’s identity provider.

## Prerequisites
Before starting the deployment, make sure you have:

- A verified [UpCloud account](https://upcloud.com) with an API enabled subaccount for creating resources.
- A hosted domain and DNS provider (e.g., Route53, GoDaddy) for assigning a subdomain to the data platform stack.
- Installed [OpenTofu](https://opentofu.org/), [kubectl](https://kubernetes.io/docs/reference/kubectl/), AWS CLI (for the S3-compatible object storage backend)

## Getting started

If you want to deploy this stack on UpCloud, start by checking out the [tutorial](docs/Tutorial.md)

## Contributing

We welcome contributions from the community! Whether it's bug reports, feature requests, or code contributions, your input is valuable to us.
Please read our [contributing guidelines](CONTRIBUTING.md) for more details on how to contribute to this repository.

## Support
If you have any questions or run into issues, feel free to open an issue in this Github repo or reach out to `niels.claeys@dataminded.com` or anyone else at Dataminded.

If you want guidance on how to extend this stack or make it production ready, you can reach out to [DataMinded](https://www.dataminded.com/contact).

[contributors-shield]: https://img.shields.io/github/contributors/datamindedbe/demo-upcloud-data-platform.svg?style=for-the-badge

[contributors-url]: https://github.com/datamindedbe/demo-upcloud-data-platform/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/datamindedbe/demo-upcloud-data-platform.svg?style=for-the-badge

[forks-url]: https://github.com/datamindedbe/demo-upcloud-data-platform/network/members

[license-shield]: https://img.shields.io/github/license/datamindedbe/demo-upcloud-data-platform.svg?label=license&style=for-the-badge

[license-url]: https://github.com/datamindedbe/demo-upcloud-data-platform/blob/master/LICENSE.md