terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
  }
}
resource "helm_release" "opa" {
  chart = "${path.module}/helm/opa-kube-mgmt"
  name  = "opa"
  namespace = "opa"
  max_history = 10
  values = [
    <<EOF
logLevel: debug
logFormat: json
policyDirectory: /var/lib/opa/policies
useHttps: false

image:
  repository: nilli9990/demo-upcloud-opa
  tag: "latest"
  pullPolicy: Always

extraArgs:
  - --set=decision_logs.console=true

extraEnv:
  - name: TRINO_LAKEKEEPER_CATALOG_NAME
    value: "iceberg"
  - name: LAKEKEEPER_LAKEKEEPER_WAREHOUSE
    value: "iceberg"

authz:
  enabled: false
mgmt:
  enabled: false
EOF
  ]
}