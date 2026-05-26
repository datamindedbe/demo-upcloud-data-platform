resource "helm_release" "lakekeeper" {
  repository = "https://lakekeeper.github.io/lakekeeper-charts"
  chart      = "lakekeeper"
  version    = "0.10.1"
  name       = "lakekeeper"
  namespace  = "services"
  wait       = false
  values = [
    <<EOF
catalog:
  extraEnvFrom:
    - secretRef:
        name: lakekeeper-custom-secrets #overwrite the external database credentials with our own settings
  extraEnv:
    - name: LAKEKEEPER__UI__OPENID_CLIENT_ID
      valueFrom:
        secretKeyRef:
          name: lakekeeper-ui-oidc
          key: CLIENT_ID
  ingress:
    enabled: true
    host: lakekeeper.${var.domain}
    ingressClassName: traefik
    annotations:
      traefik.ingress.kubernetes.io/router.tls.certresolver: "letsencrypt"
      traefik.ingress.kubernetes.io/router.tls: "true"
postgresql:
  enabled: false
authz:
  backend: openfga
internalOpenFGA: true

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