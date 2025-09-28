terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
  }
}
resource "helm_release" "zitadel" {
  repository = "https://charts.zitadel.com"
  chart      = "zitadel"
  name       = "zitadel"
  namespace  = "services"
  version    = "8.13.4"
  values = [
    <<EOF
zitadel:
  masterkey: x123456789012345678901234567891y
  configmapConfig:
    ExternalSecure: true
    ExternalDomain: "zitadel.${var.domain}"
    TLS:
      Enabled: false
    FirstInstance:
      Org:
        Human:
          Username: "admin"
          Password: "SecureP@ssw0rd!"
          FirstName: "Default"
          LastName: "Admin"
          Email:
            Address: ${var.zitadel_admin_email}
            Verified: true
  configSecretName: zitadel-credentials
  configSecretKey: config.yaml
ingress:
  enabled: true
  className: traefik
  annotations:
    # Enable TLS with Let's Encrypt
    traefik.ingress.kubernetes.io/router.tls.certresolver: "letsencrypt"
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    traefik.ingress.kubernetes.io/router.tls: "true"
  hosts:
    - host: "zitadel.${var.domain}"
      paths:
        - path: /
          pathType: Prefix
service:
  annotations:
    traefik.ingress.kubernetes.io/service.serversscheme: h2c
EOF
  ]
}