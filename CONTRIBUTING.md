# Contributing

Thank you for helping improve this GitHub Actions OIDC AWS deployment reference.

This repository contains public examples for IAM, trust policies, and deployment workflows. Changes should keep the examples safe, easy to understand, and free of private account data.

## Good Contributions

Useful improvements include:

- clearer README explanations
- safer IAM or trust policy examples
- troubleshooting notes based on common deployment failures
- workflow comments that explain security-sensitive settings
- documentation links, examples, and diagrams
- repository hygiene such as issue templates or PR templates

## Safety Principles

When changing IAM, OIDC, or workflow examples:

- Do not add long-lived AWS access keys or static credentials.
- Do not use real AWS account IDs, role ARNs, customer names, or private repository names.
- Keep production examples scoped to protected branches, tags, or GitHub environments.
- Prefer least-privilege permissions over broad managed policies.
- Keep placeholder values obvious, for example `ACCOUNT_ID`, `OWNER`, `REPOSITORY`, and `ROLE_NAME`.
- Explain why a permission or trust condition is required when it may look broad.

## Before Opening a Pull Request

Check that:

- Markdown renders clearly.
- New files are linked from the README when useful.
- Examples remain copyable after replacing placeholders.
- Security guidance does not encourage bypassing OIDC, branch scoping, environment approvals, or least privilege.
- No private logs, account identifiers, credentials, or production details were included.

## Pull Request Scope

Keep pull requests small and focused. A good PR should usually cover one of these:

- one documentation improvement
- one workflow example improvement
- one IAM policy or trust policy clarification
- one repository hygiene improvement

If a change affects both workflow behaviour and IAM permissions, describe the relationship clearly in the PR summary.

## Review Notes

For documentation-only changes, no runtime tests are expected. For workflow or IAM snippets, review the syntax and describe any validation performed in the pull request.
