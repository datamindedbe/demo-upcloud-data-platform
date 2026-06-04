# s3-benchmark — build the image and run it as a Job on the k8s cluster.
#
# Quick start:
#   make run          # (re)deploy the Job and stream its output until it finishes
#
# Override any variable on the command line, e.g.:
#   make run NAMESPACE=benchmarks KUBECONFIG=~/.kube/config

# --- Configuration -----------------------------------------------------------

IMAGE      ?= ghcr.io/datamindedbe/demo-inno26q2-sentinel-opencloud-integration/s3-benchmark:latest
PLATFORM   ?= linux/amd64
KUBECONFIG ?= ../infra/.kubeconfig.yml
NAMESPACE  ?= default

# Two job variants. run_without/run_with select between them.
WITHOUT_JOB  ?= s3-benchmark
WITHOUT_FILE ?= k8s-job-without-sentinel.yaml
WITH_JOB     ?= s3-benchmark-sentinel
WITH_FILE    ?= k8s-job-with-sentinel.yaml

# Active job — defaults to the "without" variant; overridden per target below.
JOB        ?= $(WITHOUT_JOB)
K8S_JOB    ?= $(WITHOUT_FILE)

# Benchmark workload — templated into the Job manifest at deploy time.
# Override on the command line, e.g.: make run_without BIG_FILE_SIZE_MB=500 PROCESSES=8
BIG_FILE_SIZE_MB ?= 100
SMALL_FILE_COUNT ?= 100
PROCESSES        ?= 4

# Credentials for the GHCR pull secret. Prefer a read-only PAT (read:packages)
# over your full gh token: make pull-secret GHCR_TOKEN=ghp_xxx
GHCR_USER  ?= JeroenBosmans
GHCR_TOKEN ?= $(shell gh auth token)

KUBECTL = kubectl --kubeconfig=$(KUBECONFIG) -n $(NAMESPACE)

.DEFAULT_GOAL := help

# --- Targets -----------------------------------------------------------------

.PHONY: help
help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build the image for the cluster's architecture (linux/amd64)
	docker buildx build --platform $(PLATFORM) -t $(IMAGE) --load .

.PHONY: push
push: ## Build for linux/amd64 and push to GHCR (needs write:packages)
	docker buildx build --platform $(PLATFORM) -t $(IMAGE) --push .

.PHONY: pull-secret
pull-secret: ## Create/update the GHCR image pull secret on the cluster
	$(KUBECTL) create secret docker-registry ghcr-pull-secret \
		--docker-server=ghcr.io \
		--docker-username=$(GHCR_USER) \
		--docker-password='$(GHCR_TOKEN)' \
		--dry-run=client -o yaml | $(KUBECTL) apply -f -

.PHONY: deploy
deploy: ## (Re)create the Job on the cluster (workload values templated in)
	$(KUBECTL) delete job $(JOB) --ignore-not-found
	sed -e 's#@@BIG_FILE_SIZE_MB@@#$(BIG_FILE_SIZE_MB)#g' \
	    -e 's#@@SMALL_FILE_COUNT@@#$(SMALL_FILE_COUNT)#g' \
	    -e 's#@@PROCESSES@@#$(PROCESSES)#g' \
	    $(K8S_JOB) | $(KUBECTL) apply -f -

.PHONY: run_without
run_without: JOB = $(WITHOUT_JOB)
run_without: K8S_JOB = $(WITHOUT_FILE)
run_without: _run ## Run the benchmark directly against object storage (no sentinel)

.PHONY: run_with
run_with: JOB = $(WITH_JOB)
run_with: K8S_JOB = $(WITH_FILE)
run_with: _run ## Run the benchmark through the s3 sentinel proxy

.PHONY: _run
_run: deploy
	@echo "==> Waiting for pod to be scheduled..."
	@until $(KUBECTL) get pod -l job-name=$(JOB) -o name 2>/dev/null | grep -q pod/; do sleep 1; done
	$(KUBECTL) wait --for=condition=ready pod -l job-name=$(JOB) --timeout=120s 2>/dev/null || true
	@echo "==> Streaming logs..."
	$(KUBECTL) logs -f job/$(JOB)

.PHONY: logs
logs: ## Show the current Job's logs
	$(KUBECTL) logs job/$(JOB)

.PHONY: status
status: ## Show Job and pod status
	$(KUBECTL) get job $(JOB) -o wide || true
	$(KUBECTL) get pods -l job-name=$(JOB) -o wide || true

.PHONY: clean
clean: ## Delete the Job from the cluster
	$(KUBECTL) delete job $(JOB) --ignore-not-found
