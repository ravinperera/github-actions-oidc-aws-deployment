# OIDC Trust Policy

A GitHub Actions OIDC trust policy controls which GitHub workflows are allowed to assume an AWS IAM role.

## Important Claims

| Claim | Purpose |
| --- | --- |
| `aud` | Should normally equal `sts.amazonaws.com` for AWS role assumption. |
| `sub` | Identifies the GitHub repository, branch, tag, pull request, or environment. |
| `repository` | Can be used to restrict access to one repository. |
| `ref` | Can be used to restrict access to a branch or tag. |

## Example Subject Conditions

Allow only the `main` branch:

```text
repo:ravinperera/github-actions-oidc-aws-deployment:ref:refs/heads/main
```

Allow a GitHub environment:

```text
repo:ravinperera/github-actions-oidc-aws-deployment:environment:production
```

## Recommended Pattern

Use separate roles per environment:

- `example-dev-github-actions-role`
- `example-staging-github-actions-role`
- `example-prod-github-actions-role`

For production, prefer GitHub environments with required reviewers. This adds approval control before the job can request AWS credentials.
