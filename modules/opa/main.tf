resource "helm_release" "opa" {
  chart       = "${path.module}/helm/opa-kube-mgmt"
  name        = "opa"
  namespace   = "opa"
  max_history = 10
  values = [
    <<EOF
logLevel: debug
logFormat: json
policyDirectory: /var/lib/opa/policies
useHttps: false

image:
  repository: nilli9990/demo-upcloud-opa
  tag: "1.16.0"
  pullPolicy: Always

extraArgs:
  - --set=decision_logs.console=true

extraEnv:
  - name: TRINO_LAKEKEEPER_CATALOG_NAME
    value: "iceberg"
  - name: LAKEKEEPER_LAKEKEEPER_WAREHOUSE
    value: "iceberg"
  - name: LAKEKEEPER_CLIENT_ID
    valueFrom:
      secretKeyRef:
        name: opa-lakekeeper-credentials
        key: CLIENT_ID
  - name: LAKEKEEPER_CLIENT_SECRET
    valueFrom:
      secretKeyRef:
        name: opa-lakekeeper-credentials
        key: CLIENT_SECRET
  - name: LAKEKEEPER_URL
    value: "http://lakekeeper.services.svc.cluster.local:8181"
  - name: LAKEKEEPER_SCOPE
    value: "openid"
  - name: LAKEKEEPER_TOKEN_ENDPOINT
    value: "https://zitadel.${var.domain}/oauth/v2/token"

authz:
  enabled: false
mgmt:
  enabled: false
EOF
  ]
}