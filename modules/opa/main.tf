terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
  }
}
resource "helm_release" "opa" {
  chart = "opa-kube-mgmt"
  repository = "https://open-policy-agent.github.io/kube-mgmt/charts"
  version = "9.1.0"
  name  = "opa"
  namespace = "opa"
  values = [
    <<EOF
opa:
  args:
    - run
    - --server
    - --addr=0.0.0.0:8181
    - --log-level=debug
    - --log-format=json
    - --set=decision_logs.console=true
    - /var/lib/opa/policies
useHttps: false

image:
  repository: nilli9990/demo-upcloud-opa
  tag: "latest"
  pullPolicy: Always

extraArgs:
  - --log-level=debug
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