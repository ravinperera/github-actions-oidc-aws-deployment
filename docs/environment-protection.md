# Environment Protection for OIDC Deployments

GitHub Actions OIDC removes the need for long-lived AWS access keys, but it does not replace deployment governance. Production and staging deployments should still use GitHub Environments, branch rules, and reviewer gates.

## Recommended Environment Model

| Environment | Typical source | Required controls |
| --- | --- | --- |
| `dev` | feature branches or `develop` | scoped AWS role, short session duration, limited permissions |
| `staging` | `staging` branch or release candidate | environment protection, deployment history, smoke test evidence |
| `production` | `main`, release branch, or signed tag | required reviewers, protected branch, restricted AWS role, rollback plan |

## GitHub Environment Settings

For each deployment environment:

1. Create a GitHub Environment with the same name used by the workflow.
2. Add required reviewers for sensitive environments such as staging and production.
3. Restrict which branches and tags can deploy to the environment.
4. Keep environment variables separate from repository-wide variables.
5. Avoid storing static AWS keys as secrets; OIDC should assume roles at runtime.

## AWS Trust Policy Alignment

The IAM role trust policy should match the GitHub deployment path. For production, prefer conditions that restrict both repository and branch or tag source.

Example claim patterns:

```text
repo:OWNER/REPO:ref:refs/heads/main
repo:OWNER/REPO:ref:refs/tags/v*
repo:OWNER/REPO:environment:production
```

Use the narrowest condition that still supports the release process. Avoid wildcard repository or branch conditions for production roles.

## Reviewer Gate Checklist

Before approving a production deployment, reviewers should confirm:

- the workflow is running from the expected branch or tag;
- the Terraform plan or deployment preview has been reviewed;
- the AWS role being assumed matches the target environment;
- rollback steps are understood;
- no static AWS credentials were introduced in repository or environment secrets.

## Rollback Considerations

OIDC controls access, but rollback still depends on the deployment mechanism. Keep rollback instructions close to the workflow documentation and ensure production reviewers know whether rollback means redeploying a previous artifact, reverting infrastructure, or restoring configuration.

## Common Mistakes

- Reusing one AWS role across all environments.
- Allowing feature branches to assume production roles.
- Using GitHub Environments but not adding required reviewers.
- Adding static AWS access keys as a fallback secret.
- Using broad trust policy wildcards such as `repo:OWNER/*` for deployment roles.
