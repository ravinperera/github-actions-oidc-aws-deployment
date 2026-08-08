# Security Policy

## Reporting a vulnerability

Please do not disclose a suspected vulnerability, exploit path, credential, AWS account identifier, private log, or other sensitive evidence in a public issue or pull request.

Use GitHub's **Report a vulnerability** option for this repository when it is available so the report can be discussed privately. If private vulnerability reporting is not available, open a public issue containing only a request for a private contact path; do not include the sensitive details themselves.

A useful private report should include:

- the affected file, example, or documented pattern;
- the security impact and conditions required to reproduce it;
- minimal reproduction steps using placeholders or redacted values;
- any suggested mitigation, if known.

## Accidental credential exposure

If an AWS access key, GitHub token, OIDC-related secret, or other credential is exposed, treat the credential as compromised rather than relying on deletion from Git history.

1. Revoke, rotate, or disable the exposed credential immediately in the system that issued it.
2. Review relevant AWS CloudTrail, GitHub audit, and workflow activity for unexpected use.
3. Remove the sensitive value from the repository and any associated artifacts or logs where practical.
4. Follow the organisation's incident-response process before restoring access.

Do not paste the credential into an issue while asking for help.

## Scope and expectations

This repository is a public reference implementation for GitHub Actions OIDC and AWS deployment patterns. Its examples use placeholders and are not a substitute for an environment-specific IAM, trust-policy, network, change-management, or production-security review.

Security reports about the repository's examples, validation logic, documentation, or workflow patterns are welcome. Reports about unrelated third-party services should be sent to the relevant vendor or project.
