#!/usr/bin/env bash
set -euo pipefail

# Detect root directory
if [[ "$(basename "$(pwd)")" == "scripts" ]]; then
  ROOT_DIR="$(dirname "$(pwd)")"
else
  ROOT_DIR="$(pwd)"
fi

# Find all directories containing *.tf files (likely Terraform modules)
MODULE_DIRS=$(find "$ROOT_DIR/modules" -type f -name "*.tf" -exec dirname {} \; | sort -u)

for dir in $MODULE_DIRS; do
  echo "Generating docs for module: $dir"
  (cd "$dir" && terraform-docs markdown --output-file README.md ./)
done

INFRA_DIRS=$(find "$ROOT_DIR/infra" -type f -name "*.tf" -exec dirname {} \; | sort -u)

for dir in $INFRA_DIRS; do
  echo "Generating docs for module: $dir"
  (cd "$dir" && terraform-docs markdown --output-file README.md ./)
done

echo "All module readmes have been generated!"