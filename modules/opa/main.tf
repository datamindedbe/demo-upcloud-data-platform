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
  repository: openpolicyagent/opa
  tag: "1.3.0" # Specify the OPA version you want to use
  pullPolicy: Always

extraArgs:
  - --log-level=debug
  - --set=decision_logs.console=true

authz:
  enabled: false
mgmt:
  enabled: false
EOF
  ]
}