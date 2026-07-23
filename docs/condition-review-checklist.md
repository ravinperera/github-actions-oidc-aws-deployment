# OIDC Condition Review Checklist

Use this checklist before allowing a GitHub Actions workflow to assume an AWS IAM role. Replace every placeholder with values owned and reviewed by your organisation.

## Repository scope

- [ ] Restrict the trust policy to the intended GitHub organisation and repository.
- [ ] Confirm renamed, transferred, archived, or forked repositories cannot match the condition unexpectedly.
- [ ] Avoid organisation-wide wildcards unless the role is intentionally shared and has tightly limited permissions.

Safe example:

```json
"token.actions.githubusercontent.com:sub": "repo:example-org/example-repo:ref:refs/heads/main"
```

Risky example:

```json
"token.actions.githubusercontent.com:sub": "repo:example-org/*"
```

## Branch, tag, and pull-request scope

- [ ] Restrict branch-based deployments to the exact protected branch where practical.
- [ ] Review tag patterns separately from branch patterns.
- [ ] Do not allow pull-request subjects to assume deployment roles unless that access is explicitly required.
- [ ] Check that wildcard matching cannot include similarly named branches or tags.

Safe example:

```json
"token.actions.githubusercontent.com:sub": "repo:example-org/example-repo:ref:refs/heads/main"
```

Risky example:

```json
"token.actions.githubusercontent.com:sub": "repo:example-org/example-repo:ref:refs/heads/*"
```

## Environment scope

- [ ] Prefer a GitHub environment for sensitive deployments such as production.
- [ ] Configure required reviewers, deployment branch rules, and environment protection separately in GitHub.
- [ ] Confirm the trust policy subject uses the exact environment name, including case.
- [ ] Ensure the workflow job declares the same environment before requesting the OIDC token.

Safe example:

```json
"token.actions.githubusercontent.com:sub": "repo:example-org/example-repo:environment:production"
```

Risky pattern:

- A production role trusts a branch subject but the workflow has no protected GitHub environment or approval gate.

## Audience scope

- [ ] Require the AWS STS audience.
- [ ] Confirm the workflow and AWS trust policy use the same audience value.
- [ ] Do not remove the audience condition merely to make authentication succeed.

Recommended condition:

```json
"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
```

## IAM and workflow checks

- [ ] Use a separate AWS role per environment or security boundary.
- [ ] Keep the role permissions narrower than the trust relationship.
- [ ] Grant `id-token: write` only to jobs that need AWS authentication.
- [ ] Pin third-party actions to reviewed versions or commit SHAs according to your dependency policy.
- [ ] Prevent untrusted pull-request code from reaching privileged deployment jobs.
- [ ] Review reusable workflows and their callers because both can affect the resulting token claims.

## Validation before adoption

- [ ] Inspect the final rendered IAM trust policy, not only the Terraform variables used to generate it.
- [ ] Test an allowed workflow and confirm role assumption succeeds.
- [ ] Test at least one disallowed branch, repository, or environment and confirm role assumption fails.
- [ ] Review CloudTrail events for `AssumeRoleWithWebIdentity` and verify the expected role and repository context.
- [ ] Record the reviewer, date, approved conditions, and reason for any wildcard.

## Example review record

```text
Role: example-prod-github-actions-role
Repository: example-org/example-repo
Subject: repo:example-org/example-repo:environment:production
Audience: sts.amazonaws.com
GitHub environment protections reviewed: yes
Wildcard exceptions: none
Reviewer: <name>
Review date: <YYYY-MM-DD>
```

This checklist is a starting point. Repository settings, GitHub environment protections, workflow permissions, and the AWS role's permission policy must also be reviewed together.