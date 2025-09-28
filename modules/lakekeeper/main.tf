resource "helm_release" "lakekeeper" {
  repository = "https://lakekeeper.github.io/lakekeeper-charts"
  chart      = "lakekeeper"
  version    = "0.6.0"
  name       = "lakekeeper"
  namespace  = "services"
  wait       = false
  values = [
    <<EOF
catalog:
  image:
    tag: v0.9.5
  extraEnvFrom:
    - secretRef:
        name: lakekeeper-custom-secrets #overwrite the external database credentials with our own settings
  ingress:
    enabled: true
    host: lakekeeper.${var.domain}
    ingressClassName: traefik
    annotations:
      traefik.ingress.kubernetes.io/router.tls.certresolver: "letsencrypt"
      traefik.ingress.kubernetes.io/router.tls: "true"
postgresql:
  enabled: false

externalDatabase:
  type: postgresql
  host_read: # used from lakekeeper-custom-secrets
  port: # used from lakekeeper-custom-secrets
  user: # used from lakekeeper-custom-secrets
  database: # used from lakekeeper-custom-secrets
EOF
  ]
  timeout = 500
}