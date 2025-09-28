resource "helm_release" "traefik" {
  chart      = "traefik"
  repository = "https://helm.traefik.io/traefik"
  version    = "v35.1.0"
  name       = "traefik"
  namespace  = "traefik"
  values = [
    <<EOF
# Enable dashboard access (consider security implications for production)
ingressRoute:
  dashboard:
    enabled: true
    # Use the default entrypoint for the dashboard
    entryPoints:
      - websecure
    # Define the matching rule for the dashboard route
    matchRule: Host(`traefik.${var.domain}`)
  tls:
    certResolver: letsencrypt

service:
  enabled: true
  type: LoadBalancer

  annotations:
    # TODO: check that when recreating the service, the backend members are filled in automatically now that we use the name of the nodePorts.
    service.beta.kubernetes.io/upcloud-load-balancer-config: |
      {
        "plan": "development",
        "frontends": [
            {
              "name": "http",
              "mode": "tcp",
              "default_backend": "web",
              "port" : 80,
              "networks": [
                {
                  "name": "public-IPv4"
                },
                {
                  "name": "private-IPv4"
                }]
              },
            {
              "name": "https",
              "mode": "tcp",
              "port" : 443,
              "default_backend": "websecure",
              "networks": [
              {
                "name": "public-IPv4"
              },
              {
                "name": "private-IPv4"
              }]
            }
        ],
        "backends": [
          {
            "name": "websecure",
            "properties": {
              "timeout_server": 60
            }
          },
          {
            "name": "web",
            "properties": {
              "timeout_server": 60
            }
          }
        ]
      }

# Enable Kubernetes providers
providers:
  kubernetesCRD:
    enabled: true # Enable CRD provider (for IngressRoute, ServersTransport, etc.)
  kubernetesIngress:
    enabled: true

ports:
  web:
    redirections:
      entryPoint:
        to: websecure
        scheme: https
        permanent: true
    port: 8000
    protocol: TCP
    exposedPort: 80
  websecure:
    port: 8443
    protocol: TCP
    exposedPort: 443
    tls:
      enabled: true

# add some middleware to serve the acme challenge over HTTP
middleware:
  skip-acme-redirect:
    redirectRegex:
      regex: "^/\\.well-known/acme-challenge/(.*)"
      replacement: "/.well-known/acme-challenge/$1"
      permanent: false

routers:
  acme-challenge:
    entryPoints:
      - web
    rule: "PathPrefix(`/.well-known/acme-challenge/`)"
    service: api@internal
    priority: 100
    middlewares:
      - skip-acme-redirect@internal

# Configure Let's Encrypt ACME
certificatesResolvers:
  letsencrypt:
    acme:
      # ACME CA server to use
      caServer: https://acme-v02.api.letsencrypt.org/directory
      # Email address used for registration
      email: "niels.claeys@dataminded.com"
      # File or key used for certificates storage
      storage: /data/acme.json
      # HTTP challenge
      httpChallenge:
        entryPoint: web

# Persistence for ACME certificates
persistence:
  enabled: true
  accessMode: ReadWriteOnce
  size: 1Gi
  path: /data
  annotations: {}
# lol you need to chmod 600 if you want acme.json to be accessible
deployment:
  initContainers:
    - name: volume-permissions
      image: busybox:latest
      command: ["sh", "-c", "ls -la /; touch /data/acme.json; chmod -v 600 /data/acme.json"]
      volumeMounts:
      - mountPath: /data
        name: data
podSecurityContext:
fsGroup: 65532
fsGroupChangePolicy: "OnRootMismatch"

additionalArguments:
  - "--log.level=DEBUG"
EOF
  ]
  timeout = 900
}