terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = "2.16.1"
    }
  }
}
resource "helm_release" "trino" {
  repository = "https://trinodb.github.io/charts/"
  chart      = "trino"
  version    = "1.39.0"
  name       = "trino"
  namespace  = "services"
  values = [
    <<EOF
additionalConfigProperties: []
envFrom:
  - secretRef:
      name: s3-credentials
    prefix: S3_
  - secretRef:
      name: pg-credentials
    prefix: PG_
  - secretRef:
      name: trino-oidc
    prefix: OAUTH2_
server:
  config:
    authenticationType: OAUTH2
catalogs:
  iceberg: |
    connector.name=iceberg
    iceberg.catalog.type=rest
    iceberg.rest-catalog.uri=http://lakekeeper.services.svc.cluster.local:8181/catalog
    iceberg.rest-catalog.warehouse=iceberg
    fs.native-s3.enabled=true
    s3.endpoint=$${ENV:S3_ENDPOINT}
    s3.region=$${ENV:S3_REGION}
    s3.aws-access-key=$${ENV:S3_ACCESS_KEY_ID}
    s3.aws-secret-key=$${ENV:S3_SECRET_ACCESS_KEY}
    iceberg.rest-catalog.security=NONE
    iceberg.rest-catalog.vended-credentials-enabled=true

coordinator:
  additionalConfigFiles:
    config.properties: |
      catalog.management=static
      http-server.http.enabled=true
      http-server.http.port=8080
      discovery.uri=http://trino:8080
      internal-communication.shared-secret=123456
      http-server.process-forwarded=true
  resources:
    requests:
      cpu: 100m
      memory: 128Mi

worker:
  additionalConfigFiles:
    config.properties: |
      http-server.authentication.type=oauth2
      internal-communication.shared-secret=123456
      discovery.uri=http://trino.services.svc:8080
      http-server.http.enabled=true
      http-server.http.port=8080
      http-server.authentication.oauth2.scopes=openid
      http-server.authentication.oauth2.issuer=https://zitadel.${var.domain}
      http-server.authentication.oauth2.client-id=$${ENV:OAUTH2_CLIENT_ID}
      http-server.authentication.oauth2.client-secret=$${ENV:OAUTH2_CLIENT_SECRET}
  resources:
    requests:
      cpu: 100m
      memory: 128Mi

ingress:
  enabled: true
  className: traefik
  annotations:
    # Enable TLS with Let's Encrypt
    traefik.ingress.kubernetes.io/router.tls: "true"
    traefik.ingress.kubernetes.io/router.tls.certresolver: "letsencrypt"
  hosts:
    - host: trino.${var.domain}
      paths:
        - path: /
          pathType: Prefix

accessControl:
  type: properties
  properties: |
    access-control.name=opa
    opa.log-requests=true
    opa.log-responses=true
    opa.policy.uri=http://opa-opa-kube-mgmt.opa.svc:8181/v1/data/trino/allow
    opa.policy.batched-uri=http://opa-opa-kube-mgmt.opa.svc:8181/v1/data/trino/batch
EOF
  ]
  timeout = 500
}