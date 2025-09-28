.PHONY: lint generate-readme pre-commit

# Run Terraform linting and validation
lint:
	@echo "==> Running terraform fmt..."
	tofu fmt -recursive -check
	@echo "==> Running terraform validate..."
	tofu validate
	@echo "==> Running tflint..."
	tflint --recursive

# Generate README files from Terraform modules
generate-readme:
	@echo "==> Generating README.md from Terraform modules..."
	./scripts/generate-readme.sh;

# Run all checks before opening a PR
pre-commit: lint generate-readme
	@echo "✅ All checks passed!"