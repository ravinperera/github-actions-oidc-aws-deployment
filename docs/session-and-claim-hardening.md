# OIDC Session and Claim Hardening

A working OIDC trust policy is only the starting point. Production roles should also constrain who may request credentials, which workflow context is accepted, and how long the resulting session remains usable.

## Claims to Validate

AWS IAM evaluates claims from the GitHub-issued token through trust-policy conditions.

- `aud`: require `sts.amazonaws.com` for standard AWS federation.
- `sub`: restrict the repository and the intended branch, tag, pull-request context, or GitHub environment.
- Repository ownership: avoid broad organization-wide subjects unless the role is intentionally shared.
- Environment subjects: prefer a protected GitHub environment for production because the subject can be tied to that environment.
- Reusable workflows: remember that the caller repository determines the normal subject claim. Do not assume that hosting a reusable workflow in a trusted repository automatically makes every caller trusted.

Example condition shape:

```json
{
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
    "token.actions.githubusercontent.com:sub": "repo:ORG/REPOSITORY:environment:production"
  }
}
```

Use `StringLike` only when a wildcard is genuinely required. Keep the wildcard as narrow as possible and document why it exists.

## Session Duration

Set the role's maximum session duration to the shortest value that comfortably supports the deployment. A short session limits the value of credentials copied from a runner or exposed in logs.

Practical guidance:

- Start with one hour or less for normal deployments.
- Increase only for measured workflows that cannot complete reliably within the current limit.
- Separate long-running operations from routine deployments rather than giving every workflow a long session.
- Reassess the duration when deployment steps or environments change.

## Session Naming and Traceability

Use a recognizable role-session name where the action supports it. Include stable, non-secret context such as the repository, workflow, and run identifier. This makes CloudTrail investigation easier without putting user input or sensitive values into the session name.

Example:

```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
    aws-region: eu-west-2
    role-session-name: gha-${{ github.run_id }}-${{ github.run_attempt }}
```

## Additional Guardrails

- Keep workflow permissions minimal: usually `id-token: write` and `contents: read`.
- Pin third-party actions to reviewed versions or commit SHAs according to your supply-chain policy.
- Protect production environments with required reviewers and restricted deployment branches.
- Avoid exposing the OIDC token or temporary AWS credentials in logs or artifacts.
- Use separate roles for materially different environments or deployment capabilities.

## Validation Checklist

- [ ] The audience is restricted to `sts.amazonaws.com`.
- [ ] The subject matches only the intended repository and deployment context.
- [ ] Wildcards are narrow, justified, and reviewed.
- [ ] Production uses a protected GitHub environment where practical.
- [ ] Reusable-workflow callers are explicitly considered.
- [ ] Session duration is no longer than the deployment requires.
- [ ] Session names support CloudTrail investigation without exposing sensitive data.
- [ ] Workflow permissions and action dependencies are reviewed.
