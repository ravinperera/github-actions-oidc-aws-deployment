# Security Notes

## Avoid Static AWS Keys

Do not store `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in GitHub secrets for long-running deployment access. Prefer OIDC with short-lived credentials.

## Scope Trust Policies

A weak trust policy can accidentally allow more workflows than intended. Restrict by:

- GitHub owner
- repository
- branch
- tag
- GitHub environment

## Separate Environments

Use separate AWS roles for development, staging, and production. Production should not share the same deployment permissions as development.

## Keep IAM Permissions Narrow

Avoid `AdministratorAccess` for deployment roles. Start with the resources the workflow actually needs:

- Terraform state bucket and lock table
- ECS service update permissions
- ECR read/push permissions where required
- `iam:PassRole` only for approved ECS roles
- read-only access to required deployment inputs

## Auditability

AWS CloudTrail will show `AssumeRoleWithWebIdentity` events. Keep role names and session names clear so deployment activity can be traced back to GitHub workflows.
