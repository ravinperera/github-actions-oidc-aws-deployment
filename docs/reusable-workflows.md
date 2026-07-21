# Secure Reusable Workflows with AWS OIDC

Reusable workflows reduce duplication, but they also create a trust boundary between the caller repository and the workflow repository. The called workflow does not automatically make an untrusted caller safe.

## Key Principles

- Treat the caller repository, branch, tag, or environment as the identity that must be authorised by AWS.
- Keep `permissions` explicit in both caller and called workflows; use only `id-token: write` and the minimum repository permissions required.
- Pass non-sensitive configuration as typed `workflow_call` inputs.
- Avoid `secrets: inherit` unless every inherited secret is genuinely required and the caller is trusted.
- Use protected GitHub environments for production approval and environment-scoped secrets.
- Pin shared workflows to an immutable commit SHA or a controlled release tag.
- Keep deployment roles separate by environment and capability.

## Called Workflow Example

```yaml
name: reusable-aws-deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      aws-region:
        required: true
        type: string
    secrets:
      role-arn:
        required: true

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.role-arn }}
          aws-region: ${{ inputs.aws-region }}
          role-session-name: gha-${{ github.run_id }}
      - run: ./scripts/deploy.sh
```

## Caller Example

```yaml
jobs:
  deploy-production:
    uses: trusted-org/platform-workflows/.github/workflows/aws-deploy.yml@v1
    with:
      environment: production
      aws-region: eu-west-2
    secrets:
      role-arn: ${{ secrets.AWS_PROD_ROLE_ARN }}
```

## Trust-Policy Considerations

The normal OIDC subject reflects the caller context. Restrict the AWS role to the intended caller repository and deployment context, not merely to the repository hosting the reusable workflow. Where multiple repositories are authorised, list them explicitly or use tightly controlled patterns.

Do not rely on workflow filename alone as the security boundary. Review who can modify the reusable workflow reference, the caller workflow, environment rules, and the AWS trust policy.

## Review Checklist

- [ ] Caller repositories are explicitly authorised.
- [ ] The reusable workflow reference is pinned to a reviewed version.
- [ ] Permissions are minimal and explicit.
- [ ] Secrets are passed individually rather than inherited broadly.
- [ ] Production uses environment protection and required reviewers.
- [ ] AWS roles are separated by environment or privilege level.
- [ ] Changes to caller and called workflows receive appropriate review.
