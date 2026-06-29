# OIDC Troubleshooting Guide

Use this guide when a GitHub Actions workflow cannot assume an AWS role through OIDC.

## Quick Checks

Before changing IAM, confirm the workflow and repository inputs are correct:

- The workflow has `permissions: id-token: write`.
- The role ARN points to the expected AWS account.
- The workflow is running from the branch, tag, or GitHub environment allowed by the trust policy.
- The AWS region used by the deployment matches the target resources.
- The repository owner and name in the trust policy match the real GitHub repository.

## Common Symptoms

| Symptom | Likely cause | What to check |
| --- | --- | --- |
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` | Trust policy does not match the workflow token claims | Check the `sub` and `aud` conditions in the role trust policy. |
| `No OpenIDConnect provider found` | AWS OIDC provider is missing or configured with the wrong URL | Confirm the account has an OIDC provider for `https://token.actions.githubusercontent.com`. |
| `Could not load credentials from any providers` | Workflow did not receive AWS credentials | Confirm `aws-actions/configure-aws-credentials` is configured with the correct role ARN and region. |
| Deployment works in dev but not production | Production branch or environment is not allowed | Compare the production trust policy with the workflow branch and environment. |
| Terraform can plan but not apply | IAM permissions are too narrow for the apply step | Add only the missing deployment actions instead of using broad admin access. |

## Trust Policy Claim Checks

A secure trust policy should usually validate:

- `aud` is `sts.amazonaws.com`.
- `sub` is restricted to the expected repository and branch, tag, or environment.
- Separate AWS roles are used for dev, staging, and production.

Example `sub` patterns:

```text
repo:OWNER/REPOSITORY:ref:refs/heads/main
repo:OWNER/REPOSITORY:environment:production
repo:OWNER/REPOSITORY:ref:refs/tags/v*
```

Use the narrowest pattern that still supports the deployment workflow.

## Safe Verification Steps

1. Re-run the workflow from the intended branch or environment.
2. Check the GitHub Actions job logs for the exact AWS role ARN being assumed.
3. Check AWS CloudTrail for `AssumeRoleWithWebIdentity` failures.
4. Compare the failed token context with the role trust policy conditions.
5. Update only the specific condition or permission that is blocking the expected workflow.

## What Not To Do

- Do not add long-lived AWS access keys as a workaround.
- Do not replace the deployment policy with `AdministratorAccess`.
- Do not remove branch or environment conditions from production roles.
- Do not share one production role across unrelated repositories.

## Useful References In This Repository

- `docs/trust-policy.md` explains trust policy scoping.
- `docs/workflow-design.md` explains workflow structure.
- `docs/security-notes.md` lists the main security controls.
