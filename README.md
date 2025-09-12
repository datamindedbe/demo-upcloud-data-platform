# Upcloud data-platform

This repo contains the code for building an open-source data platform on [Upcloud](https://upcloud.com/).

The platform contains the infrastructure and configuration for a lakehouse data platform based on the following open-source components:
* Trino: the distributed query engine on top (semi) structured data. It provides a SQL interface to our data.
* Lakekeeper: data catalog for Iceberg tables as wll as restricted access to Iceberg tables
* Zitadel: for identity and access management of users as well as services
* Open Policy Agent: for implementing fine-grained access control within Trino, Lakekeeper
* Airflow: for orchestration of data pipelines
* Traefik: as an ingress controller and supporting SSL termination

## Architecture

![Architecture](docs/architecture.png)

The core of the platform is a Trino cluster, providing a SQL-like interface to data. This is used by
* data engineers who can query the data via a database client
* jobs scheduled by Airflow

## Interacting with the Platform
The Data Engineers interact with the platform via the Airflow UI and via a database client connecting to Trino.

# Deploying the platform

The platform team can deploy the infrastructure in this repository using [OpenTofu](https://opentofu.org/).

## Tools needed

* [OpenTofu](https://opentofu.org/)
* [Upcloud console](https://hub.upcloud.com)
* [Kubectl](https://kubernetes.io/docs/reference/kubectl/)
* [Helm](https://helm.sh/)

## Prerequisites

* create an Upcloud account and verify it, which requires adding a credit card. This ensures that you can provision the resources needed for this project.
* make sure you have a hostname for the data platform, many of the provisioned services require SSL, which requires a valid hostname. 
  You can use your favorite DNS provider to use a subdomain of a domain that you own.

## Infra deployment

TODO