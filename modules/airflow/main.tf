resource "helm_release" "airflow" {
  chart      = "airflow"
  repository = "https://airflow.apache.org"
  version    = "v1.21.0"
  name       = "airflow"
  namespace  = "services"
  values = [
    <<EOF
executor: KubernetesExecutor

# Configuration specific to KubernetesExecutor
# kubernetes:
#   # Namespace where worker pods will run (defaults to Airflow's namespace)
#   namespace: airflow-workers

# Disable LoadBalancer service for webserver (we'll use Ingress)
apiServer:
  resources:
    requests:
      cpu: 500m
      memory: 1024Mi
  service:
    type: ClusterIP
  livenessProbe:
    timeoutSeconds: 10
    initialDelaySeconds: 60
  startupProbe:
    timeoutSeconds: 10
    periodSeconds: 20
    failureThreshold: 6
statsd:
  enabled: false
# Use the official chart's Ingress settings for the webserver
ingress:
  apiServer:
    enabled: true
    path: /
    hosts:
      - name: airflow.${var.domain}
    ingressClassName: traefik
    annotations:
      traefik.ingress.kubernetes.io/router.entrypoints: websecure
      traefik.ingress.kubernetes.io/router.tls: "true"
      traefik.ingress.kubernetes.io/router.tls.certresolver: "letsencrypt"

dags:
  persistence:
    enabled: false  # Git sync and PVCs are mutually exclusive for DAGs

  gitSync:
    enabled: true
    repo: "https://github.com/datamindedbe/demo-upcloud-data-platform.git"  # Replace with your repo
    branch: "demo"  # Or whatever branch you want
    subPath: "usecase/dags"  # Path within the repo where DAGs are stored
    depth: 1
    rev: HEAD
    wait: 60  # Sync interval in seconds

triggerer:
  enabled: false
  replicas: 0

redis:
  enabled: false
reateUserJob:
  useHelmHooks: false
  applyCustomEnv: false
migrateDatabaseJob:
  useHelmHooks: false
  applyCustomEnv: false
logs:
  emptyDirConfig:
    medium: "Memory"
    sizeLimit: "1Gi"
  persistence:
    enabled: false
EOF
  ]
  timeout = 300
  wait    = false
}