# GitHub Actions OIDC AWS Deployment Pattern

Secure GitHub Actions to AWS deployment pattern using OIDC, IAM roles, and multi-environment workflows.

This repository demonstrates how to deploy to AWS from GitHub Actions without storing long-lived AWS access keys in GitHub secrets. It uses GitHub's OIDC identity token to assume environment-specific AWS IAM roles at runtime.

## Five-Minute Quick Start

Use this as a setup order, not as production-ready copy and paste. Review every trust condition and deployment permission for your own repository and AWS account.

### 1. Choose the deployment identity boundaries

Replace these placeholders before provisioning anything:

| Placeholder | Purpose | Example |
| --- | --- | --- |
| `<github-organisation>` | GitHub owner allowed to request credentials | `example-org` |
| `<repository>` | Repository allowed to assume the AWS role | `example-service` |
| `<branch>` | Branch allowed by the trust policy | `main` |
| `<environment>` | Protected GitHub environment | `prod` |
| `<aws-account-id>` | Target AWS account | `111122223333` |
| `<aws-region>` | Target AWS region | `eu-west-2` |

Keep the repository, branch, and environment conditions as narrow as the deployment process allows. Do not use wildcards simply to make the first test pass.

### 2. Provision or reuse the GitHub OIDC provider in AWS

The AWS account needs an IAM OIDC provider for `https://token.actions.githubusercontent.com` with the audience `sts.amazonaws.com`. An account normally needs this provider only once.

Review [`aws/iam/github-oidc-provider.tf`](aws/iam/github-oidc-provider.tf), confirm the current AWS and GitHub OIDC guidance, and either provision the provider or supply the ARN of an existing approved provider.

### 3. Create an environment-scoped deployment role

Configure [`aws/iam/github-oidc-role.tf`](aws/iam/github-oidc-role.tf) with:

```hcl
github_owner       = "<github-organisation>"
github_repository  = "<repository>"
allowed_branch      = "<branch>"
github_environment  = "<environment>"
environment         = "<environment>"
```

The role trust policy should validate both:

- `aud` equals `sts.amazonaws.com`;
- `sub` matches the intended repository plus branch or GitHub environment.

Then review `deployment-policy.json` and remove permissions that the deployment does not need. Use the [identity condition review checklist](docs/condition-review-checklist.md) to verify the repository, branch, tag, environment, audience, and optional defence-in-depth claims. See the [trust-policy guide](docs/trust-policy.md) for the claim patterns and review checks.

### 4. Configure the GitHub environment and workflow permissions

Create the matching GitHub environment, such as `dev`, `staging`, or `prod`. Add required reviewers for production before allowing the job to request AWS credentials.

The workflow needs only:

```yaml
permissions:
  id-token: write
  contents: read
```

`id-token: write` allows the job to request an OIDC token; it does not itself grant AWS access. AWS grants temporary credentials only after the IAM trust policy accepts the token claims.

### 5. Replace workflow placeholders and run a controlled test

In [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml), replace `<aws-account-id>` and the example service, cluster, and role names. Keep the role ARN aligned with the environment selected by the workflow.

Run the workflow first against a non-production environment with an immutable image tag. Confirm the caller identity step reports the expected account and role before enabling a real deployment action. Keep the previous known-good image or release available and review the [deployment incident and rollback guide](docs/rollback-guide.md) before enabling production deployment.

For the full separation of plan, deployment, and environment controls, see the [workflow-design guide](docs/workflow-design.md).

### Why temporary credentials are preferred

GitHub OIDC credentials are issued only for the workflow run, expire automatically, and are constrained by the IAM role's trust and permission policies. This avoids storing reusable AWS access keys in GitHub secrets and reduces the impact of accidental disclosure. Temporary credentials still require least-privilege roles, protected environments, and careful claim conditions.

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
│   ├── terraform-plan.yml
│   └── validate.yml
├── aws/iam/
│   ├── github-oidc-provider.tf
│   ├── github-oidc-role.tf
│   └── deployment-policy.json
├── docs/
│   ├── condition-review-checklist.md
│   ├── deployment-audit-evidence.md
│   ├── rollback-guide.md
│   ├── trust-policy.md
│   ├── workflow-design.md
│   ├── security-notes.md
│   ├── troubleshooting.md
│   ├── environment-protection.md
│   ├── least-privilege-iam.md
│   ├── reusable-workflows.md
│   ├── session-and-claim-hardening.md
│   └── validation-checklist.md
├── scripts/
│   └── validate_examples.py
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

- [OIDC identity condition review checklist](docs/condition-review-checklist.md)
- [Deployment audit evidence guide](docs/deployment-audit-evidence.md)
- [Deployment incident and rollback guide](docs/rollback-guide.md)
- [Trust policy guidance](docs/trust-policy.md)
- [Workflow design](docs/workflow-design.md)
- [Security notes](docs/security-notes.md)
- [Troubleshooting guide](docs/troubleshooting.md)
- [Environment protection guide](docs/environment-protection.md)
- [Least-privilege IAM guide](docs/least-privilege-iam.md)
- [Secure reusable workflow guidance](docs/reusable-workflows.md)
- [OIDC session and claim hardening](docs/session-and-claim-hardening.md)
- [OIDC deployment validation checklist](docs/validation-checklist.md)
- [Contributing guide](CONTRIBUTING.md)

## Validate Locally

The validation path is credential-free and does not call AWS. Terraform 1.6 or later is required.

```bash
python3 scripts/validate_examples.py
terraform fmt -check -recursive aws
terraform -chdir=aws/iam init -backend=false -input=false
terraform -chdir=aws/iam validate
```

The script validates JSON syntax, local Markdown links, workflow indentation, and checks workflow files for static AWS credential markers. GitHub Actions runs the same checks in [`.github/workflows/validate.yml`](.github/workflows/validate.yml) with read-only repository permission.

The examples intentionally contain placeholder account IDs, resource names, roles, regions, and ARNs. Validation confirms structure and Terraform syntax; it does not prove that the examples are deployable in a particular AWS account, that IAM permissions are least privilege for a real workload, or that current provider guidance has been independently reviewed. The separate Terraform plan workflow requires an approved AWS role and environment configuration and is not part of the credential-free validation path.

## Status

This is a public reference implementation. Account IDs, repository names, and resource ARNs use placeholders and must be replaced before use.
