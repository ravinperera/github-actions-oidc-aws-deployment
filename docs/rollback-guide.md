# Deployment Incident and Rollback Guide

This guide provides a safe, high-level response pattern for GitHub Actions deployments that fail partway through or release the wrong version.

It is intentionally platform-neutral. Adapt the commands, health checks, approval rules, and recovery steps to the AWS service being deployed.

## First Response

1. **Stop further change.** Cancel the active GitHub Actions run when it is still progressing and suspend any automatic follow-up deployment.
2. **Confirm the affected environment.** Check the workflow inputs, branch or tag, GitHub environment, AWS account, region, and assumed role.
3. **Preserve evidence.** Retain the workflow URL, commit SHA, deployment identifier, relevant logs, timestamps, and observed impact.
4. **Use the approved incident path.** Notify the service owner and follow the environment's incident and change-management process.
5. **Do not improvise permissions.** Do not weaken the OIDC trust policy, bypass environment approvals, or add long-lived AWS credentials to recover faster.

## Cancel or Pause the Workflow

Cancel the workflow when continuing could increase impact, overwrite a known-good version, or apply additional infrastructure changes.

Before rerunning anything, confirm:

- whether a deployment step completed before cancellation;
- whether the operation is idempotent;
- whether a Terraform apply or service update left partially changed resources;
- whether another workflow run is queued for the same environment; and
- whether concurrency controls prevent overlapping deployments.

A cancelled workflow does not automatically reverse changes already made in AWS.

## Production Approval Controls

Production recovery should use the same or stronger controls as a normal production deployment.

- Keep the production GitHub environment protected by required reviewers.
- Require the rollback target and reason to be recorded before approval.
- Verify that the workflow is running from an authorised branch or release tag.
- Confirm the OIDC token will assume the intended production role and no broader role.
- Use a separate break-glass process only when one has already been designed, approved, logged, and tested.

Do not remove required reviewers or broaden IAM trust conditions as an incident shortcut.

## Select a Recovery Target

Prefer a previously verified artefact rather than rebuilding old source during an incident.

A suitable recovery target should be:

- immutable and uniquely identified, such as an image digest, release version, object version, or deployment revision;
- previously deployed successfully to the same environment;
- still available in the relevant registry or artefact store;
- compatible with the current database and infrastructure state; and
- supported by known configuration and secrets versions.

Avoid mutable tags such as `latest` when selecting a rollback target.

## Recovery Patterns

### Container service

Redeploy the previous known-good image digest or task definition revision, then monitor service health, load balancer targets, application errors, and deployment events.

### Static site or object deployment

Restore the previous object version or release directory, then validate cache behaviour, origin health, and public content.

### Lambda or versioned function

Move the alias or traffic configuration back to the previous published version and verify invocation errors, latency, and downstream dependencies.

### Infrastructure change

Review the actual state before applying another Terraform plan. Do not assume that reverting the Git commit will safely reverse every resource change. Generate and review a new plan, identify destructive actions, and obtain the required approval.

## Validation After Recovery

Confirm all of the following before closing the incident:

- deployment status is stable;
- health checks and synthetic tests pass;
- error rate, latency, saturation, and queue depth are within expected ranges;
- the intended version is running in every target region or service;
- no overlapping workflow remains active;
- access logs and CloudTrail show the expected role and actions; and
- business or service-owner checks are complete.

Continue monitoring for an agreed observation period after technical recovery.

## Record and Follow Up

Capture:

- incident summary and impact;
- failed and recovered deployment identifiers;
- workflow run URLs and commit SHAs;
- assumed role, AWS account, region, and environment;
- recovery decision and approver;
- validation evidence; and
- follow-up actions.

Useful preventative actions may include immutable artefact references, deployment concurrency, environment approvals, canary or blue/green releases, automated smoke tests, tested rollback workflows, and clearer runbooks.

## Important Limitations

This repository is a reference pattern. It cannot define the exact rollback command for every AWS service or application architecture. Teams should test recovery procedures in a non-production environment and maintain service-specific runbooks before relying on them during an incident.
