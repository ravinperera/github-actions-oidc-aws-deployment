# GitHub Actions Supply-Chain Hardening

OIDC removes long-lived AWS access keys from GitHub, but it does not make every workflow step trustworthy. Any action that runs in a job can potentially read the files, environment variables, tokens, and temporary AWS credentials available to that job at that point in time.

Treat third-party actions as executable dependencies and review them with the same care as application dependencies.

## Recommended review order

1. **Minimise actions.** Prefer built-in shell commands or already-approved actions when they are simple and maintainable.
2. **Prefer trusted publishers.** Review the action owner, repository history, maintenance activity, release process, and security reporting path before adoption.
3. **Inspect requested capabilities.** Check what the action reads, writes, executes, uploads, and sends over the network. Confirm the workflow token and AWS permissions are no broader than the step needs.
4. **Use immutable references for high-assurance workflows.** A full commit SHA identifies one exact revision. Tags and branches are easier to read but can move. If a workflow uses a full SHA, keep the human-readable release or version in a nearby comment so updates remain reviewable.
5. **Review updates as security changes.** Compare the old and new action revisions, especially changes to install scripts, bundled JavaScript, container images, network calls, and credential handling.
6. **Reassess execution order.** An action that runs after AWS credentials are configured has access to a more sensitive execution context than the same action running before credential acquisition.

## OIDC-specific trust boundary

The most sensitive point in an OIDC deployment job is the step that exchanges the GitHub identity token for AWS credentials. After that step succeeds, later commands and actions can inherit temporary AWS credentials according to the runner environment and action behaviour.

Where practical:

- complete checkout, formatting, static validation, and other untrusted-input processing before requesting AWS credentials;
- request AWS credentials only in jobs that actually need AWS access;
- keep the AWS role least-privileged and environment-specific;
- avoid running unnecessary marketplace or third-party actions after credential configuration;
- do not pass the OIDC token or temporary AWS credentials to child processes, artifacts, logs, or outputs unless a documented design requires it.

## Reference choices

| Reference | Benefit | Trade-off |
| --- | --- | --- |
| Full commit SHA | Immutable and reviewable as one exact revision | Requires an explicit update process and is less readable |
| Release tag such as `v4.1.0` | Easy to understand and maintain | A tag can be moved unless the publisher protects it operationally |
| Major tag such as `v4` | Convenient automatic compatible updates | Broader change surface because the referenced code can change over time |
| Branch such as `main` | Always follows latest development | Unsuitable for high-assurance deployment workflows because behaviour can change without a local workflow change |

This repository keeps its existing examples unchanged; adopters should select a reference policy that matches their assurance requirements and automate reviewed updates where appropriate.

## Pull-request checklist

Before adding or updating an action in an AWS deployment workflow, confirm:

- [ ] The action is necessary and its publisher/repository has been reviewed.
- [ ] The selected reference policy matches the environment's risk level.
- [ ] The exact revision change has been reviewed, not only the release notes.
- [ ] Workflow `permissions` remain explicit and least-privileged.
- [ ] The action does not receive AWS credentials or sensitive outputs unless required.
- [ ] The action's position relative to OIDC credential acquisition is intentional.
- [ ] Production environment approvals and IAM trust conditions remain unchanged unless separately reviewed.
- [ ] No credentials, account-specific secrets, or private logs are added to the repository.

## Unsafe patterns to avoid

- Referencing a mutable development branch for a production deployment action.
- Adding an unfamiliar action after AWS credential configuration without reviewing its code and network behaviour.
- Expanding `GITHUB_TOKEN` or AWS permissions because an action fails without first identifying the permission it actually needs.
- Allowing an automated updater to merge action-reference changes without the same review applied to other executable dependencies.
- Copying an action example that requests secrets or write permissions unrelated to the deployment task.

OIDC should be combined with dependency trust, explicit workflow permissions, environment protection, and least-privilege AWS roles. Removing static AWS keys addresses one important risk; it does not remove the software supply-chain trust boundary inside the workflow itself.
