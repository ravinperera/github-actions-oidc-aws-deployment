# Documentation Guide

Use this page as the entry point for the repository's GitHub Actions OIDC and AWS deployment guidance. The documents are grouped by the question they help answer so readers can follow the shortest useful path instead of reading every guide in sequence.

## Start Here

For a first implementation review, read these in order:

1. [Trust policy guidance](trust-policy.md) — constrain which GitHub identities may assume an AWS role.
2. [OIDC identity condition review checklist](condition-review-checklist.md) — review repository, branch, tag, environment, audience, and related claim boundaries.
3. [Least-privilege IAM guidance](least-privilege-iam.md) — reduce the permissions granted after trust is established.
4. [Workflow design](workflow-design.md) — separate validation, planning, deployment, environments, and concurrency controls.
5. [OIDC deployment validation checklist](validation-checklist.md) — verify the complete pattern before treating it as ready for use.

## Identity and Authorization

- [Trust policy guidance](trust-policy.md) — core IAM trust relationship and OIDC subject/audience expectations.
- [Identity condition review checklist](condition-review-checklist.md) — detailed review prompts for identity conditions.
- [OIDC session and claim hardening](session-and-claim-hardening.md) — session naming, claims, and tighter identity boundaries.
- [Least-privilege IAM guidance](least-privilege-iam.md) — deployment-role permission design after successful authentication.

## Workflow and Dependency Design

- [Workflow design](workflow-design.md) — job separation, environment boundaries, and concurrency choices.
- [Secure reusable workflow guidance](reusable-workflows.md) — how to preserve trust boundaries when centralising workflows.
- [GitHub Actions supply-chain hardening](action-supply-chain.md) — review third-party actions as executable dependencies and prefer immutable references where appropriate.
- [Environment protection](environment-protection.md) — approvals and environment-level deployment controls.

## Operations and Evidence

- [Deployment audit evidence](deployment-audit-evidence.md) — evidence to retain for an attributable deployment trail.
- [Deployment incident and rollback guide](rollback-guide.md) — stop conditions, rollback preparation, and recovery checks.
- [Troubleshooting](troubleshooting.md) — common OIDC, IAM, and workflow failure paths.

## Security Review

- [Security notes](security-notes.md) — concise repository-specific security reminders.
- [OIDC deployment validation checklist](validation-checklist.md) — final review before adopting the reference pattern.
- [GitHub Actions supply-chain hardening](action-supply-chain.md) — dependency trust and action-reference review.

## Suggested Reading Paths

**Adopting the pattern:** trust policy → identity condition checklist → least privilege → workflow design → environment protection → validation checklist.

**Reviewing security:** trust policy → identity condition checklist → session and claim hardening → action supply chain → validation checklist.

**Operating deployments:** workflow design → environment protection → deployment audit evidence → rollback guide → troubleshooting.

These guides describe reference controls and review practices. They do not prove that a particular AWS account, IAM role, GitHub environment, or production deployment is correctly configured. Validate the final implementation against the repository's credential-free checks and the requirements of the target environment.
