# Contributing Guidelines

Thank you for your interest in contributing to this repository!
This project contains Terraform code to setup an open-source data platform on top of UpCloud. 
Please read through the guidelines below before opening a pull request.

## Getting Started

1. Fork the repository.
2. Clone your fork locally:
```
git clone https://github.com/datamindedbe/demo-upcloud-data-platform.git
cd demo-upcloud-data-platform
```
3. Create a feature branch:

```
git checkout -b feature/my-change
```

## Development Workflow

When contributing, please follow these steps:

1. Linting

All Terraform code must pass lint checks. Run:

tofu fmt -recursive
tofu validate
tflint --recursive

2. Generate READMEs terraform modules

This repository uses terraform-docs to generate module documentation.
Before submitting a PR, run: `make generate-readme`

This ensures that all module README.md files are up to date.

## Pull Request Process

1. Ensure your branch is up to date with main:

```
git fetch origin
git rebase origin/main
```

2. Make sure that:

- Your code works by applying it on your own UpCloud account
- Linting has been run and passed
- Documentation has been generated

3. Open a pull request against main.

4. Provide a clear description of the change, including:
- The problem being solved
- Any considerations or follow-up work needed

## Code Review

- At least one reviewer must approve your PR before merging.
- Keep changes small and focused for easier reviews.
- Large or breaking changes should be discussed in an issue before starting work.

## Questions?

If you’re unsure about anything, feel free to open an issue for clarification before submitting a PR.