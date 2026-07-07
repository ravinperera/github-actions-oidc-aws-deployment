# GitHub Actions OIDC AWS Deployment Pattern

Secure GitHub Actions to AWS deployment pattern using OIDC, IAM roles, and multi-environment workflows.

This repository demonstrates how to deploy to AWS from GitHub Actions without storing long-lived AWS access keys in GitHub secrets. It uses GitHub's OIDC identity token to assume environment-specific AWS IAM roles at runtime.

## What This Demonstrates

- GitHub Actions OIDC authentication to AWS
- Environment-specific IAM roles for dev, staging, and production
- Branch and environment scoping in IAM trust policies
- Least-privilege IAM permissions for CI/CD
- Multi-environment workflow design using matrix-style inputs
- Clear separation between build, plan, and deploy stages

## Why This Pattern Matters

Long-lived AWS access keys in CI/CD systems create unnecessary risk. OIDC allows GitHub Actions to request short-lived AWS credentials only when a workflow runs, and only when the workflow matches the conditions defined in the AWS IAM role trust policy.

## Repository Structure

```text
.
├── .github/workflows/
│   ├── deploy.yml
│   └── terraform-plan.yml
├── aws/iam/
│   ├── github-oidc-provider.tf
│   ├── github-oidc-role.tf
│   └── deployment-policy.json
├── docs/
│   ├── trust-policy.md
│   ├── workflow-design.md
│   ├── security-notes.md
│   ├── troubleshooting.md
│   ├── environment-protection.md
│   ├── least-privilege-iam.md
│   └── validation-checklist.md
├── CONTRIBUTING.md
└── README.md
```

## High-Level Flow

```text
Developer push / workflow dispatch
        |
        v
GitHub Actions job
        |
        | requests OIDC token
        v
AWS IAM validates token claims
        |
        | assumes environment role
        v
Deployment job receives short-lived AWS credentials
        |
        v
Terraform / ECS / S3 / Lambda / deployment action
```

## Example Environments

| Environment | Branch Pattern | AWS Role Example |
| --- | --- | --- |
| dev | `develop` or feature branches | `github-actions-dev-role` |
| staging | `staging` | `github-actions-staging-role` |
| production | `main` or release tags | `github-actions-prod-role` |

## Key Security Controls

- No static AWS access keys in GitHub secrets
- Trust policy restricted by GitHub repository and branch/environment
- Separate AWS role per environment
- Minimal IAM permissions per deployment job
- GitHub Actions permissions explicitly scoped with `id-token: write` and `contents: read`
- Production deployments should use GitHub environments and required reviewers

## Documentation

- [Trust policy guidance](docs/trust-policy.md)
- [Workflow design](docs/workflow-design.md)
- [Security notes](docs/security-notes.md)
- [Troubleshooting guide](docs/troubleshooting.md)
- [Environment protection guide](docs/environment-protection.md)
- [Least-privilege IAM guide](docs/least-privilege-iam.md)
- [OIDC deployment validation checklist](docs/validation-checklist.md)
- [Contributing guide](CONTRIBUTING.md)

## Status

This is a public reference implementation. Account IDs, repository names, and resource ARNs use placeholders and must be replaced before use.
