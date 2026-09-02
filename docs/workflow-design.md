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

## Deployment Concurrency

Prevent two deployment runs from changing the same environment at the same time. A simple per-environment pattern is:

```yaml
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

The group should identify the deployment target closely enough that unrelated environments can continue independently while runs aimed at the same environment are serialized.

`cancel-in-progress` is a policy choice, not a universal default:

- **Validation and preview jobs:** cancellation is often useful because a newer commit supersedes an older validation run.
- **Deployments:** prefer serialization unless the deployment mechanism is explicitly designed and tested to be safely interruptible.
- **Production:** do not automatically cancel an in-flight deployment merely because a newer run was queued. Cancellation can leave a partially completed rollout, make audit evidence harder to interpret, or bypass the rollback path expected by operators.

Before adopting concurrency controls, confirm:

- [ ] The concurrency key separates `dev`, `staging`, and `prod` rather than blocking every deployment globally.
- [ ] The key cannot be influenced into colliding with an unrelated protected target.
- [ ] The deployment process has documented behaviour for queued, cancelled, and failed runs.
- [ ] Production approvals still apply to each run and are not treated as transferable between queued runs.
- [ ] Operators know whether a newer deployment should wait, replace the queued run, or trigger an explicit rollback decision.

The example workflow in this repository is intentionally left unchanged so adopters can choose a concurrency policy that matches their deployment platform and rollback design.

## Image Tagging

Avoid deploying `latest`. Use immutable values:

- Git SHA
- semantic version
- release tag

This makes rollbacks and incident investigations much easier.
