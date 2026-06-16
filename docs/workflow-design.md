# Workflow Design

This repository separates validation and deployment concerns.

## Plan Workflow

The `terraform-plan.yml` workflow validates Terraform configuration and proves the OIDC role can be assumed. In a production setup, this would also produce a Terraform plan artifact or PR comment.

## Deploy Workflow

The `deploy.yml` workflow is manually triggered and requires:

- environment
- AWS region
- immutable image tag

The job uses GitHub OIDC to assume an environment-specific AWS role.

## Environment Controls

For production systems, configure GitHub environments:

- `dev`
- `staging`
- `prod`

Then add required reviewers for `prod` so production deployment requires approval before AWS credentials are requested.

## Image Tagging

Avoid deploying `latest`. Use immutable values:

- Git SHA
- semantic version
- release tag

This makes rollbacks and incident investigations much easier.
