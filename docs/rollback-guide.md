# Deployment Incident And Rollback Guide

Use this guide when a GitHub Actions deployment fails, deploys the wrong version, or leaves an AWS service in an uncertain state. Adapt the steps to the target service and the organisation's incident and change procedures.

The priority order is:

```text
protect users and data -> stop further change -> understand current state -> restore a known-good version -> verify -> learn
```

## 1. Declare And Coordinate

- [ ] Record the affected environment, AWS account, Region, service, workflow run, commit, and image or release version.
- [ ] Name an incident owner and a deployment or rollback decision-maker.
- [ ] Use the normal incident channel and change record rather than coordinating only in workflow comments.
- [ ] Preserve the workflow logs and relevant AWS events before rerunning or deleting anything.
- [ ] Escalate immediately if there is possible data loss, credential exposure, unauthorised access, or customer impact.

## 2. Stop Further Change

### Cancel the workflow

Cancel an in-progress workflow when continuing could increase impact. Cancellation prevents later steps from starting, but it does not automatically reverse AWS changes that already completed.

After cancellation:

- [ ] Identify the last successful step.
- [ ] Check whether temporary AWS credentials have already been issued.
- [ ] Confirm whether a deployment command, Terraform apply, migration, or data operation already ran.
- [ ] Disable automatic retries or scheduled deployments until the incident owner approves them.

### Use environment protection as a control point

For production environments:

- require independent approval before the job can proceed;
- restrict deployment branches and tags;
- keep production environment administration limited and auditable;
- pause or reject pending deployments while the incident is active.

Environment approval is most useful before the job requests cloud credentials or performs a write action. It is not a rollback mechanism after a write has completed.

## 3. Establish The Current State

Do not assume the requested version is the running version. Collect evidence from both GitHub and AWS.

- [ ] Confirm the workflow input values and the commit that supplied the workflow definition.
- [ ] Confirm the AWS account, role, Region, cluster, service, function, bucket, stack, or other target.
- [ ] Inspect deployment events, task or instance health, alarms, logs, and error rates.
- [ ] Identify the currently running task definition, image digest, application version, or infrastructure revision.
- [ ] Compare the current state with the last known-good release record.
- [ ] Check whether a database or schema migration limits rollback compatibility.

Read-only ECS examples:

```bash
aws ecs describe-services \
  --cluster "<cluster>" \
  --services "<service>" \
  --region "<aws-region>"

aws ecs list-task-definitions \
  --family-prefix "<task-family>" \
  --sort DESC \
  --region "<aws-region>"
```

Use placeholders and confirm the account and Region before running any command.

## 4. Choose A Recovery Path

Use the smallest safe change that restores service.

| Situation | Preferred response |
| --- | --- |
| Workflow failed before any AWS write | Fix the verified cause and rerun in a non-production environment first. |
| New application version is unhealthy | Restore the previous immutable image or task-definition revision. |
| Deployment is still progressing and health is deteriorating | Stop further rollout and follow the service-specific rollback mechanism. |
| Infrastructure change is incomplete | Review the actual state and approved plan before any apply, import, or manual repair. |
| Database change is incompatible with the previous version | Follow the tested database recovery plan; do not blindly redeploy old application code. |
| Trust or credential scope may be compromised | Disable the affected deployment path, review CloudTrail, and follow the security incident process. |

Do not use `AdministratorAccess`, long-lived access keys, or a wider OIDC trust policy as an incident workaround.

## 5. Restore A Previous Version

### ECS or container deployment

A safe rollback normally uses an immutable, previously tested artifact:

1. Identify the last known-good task definition and image digest or release tag.
2. Confirm the image still exists in the approved registry.
3. Confirm the previous version is compatible with the current database and configuration.
4. Update the service through the approved deployment workflow or reviewed service-specific procedure.
5. Monitor deployment events, target health, task health, alarms, logs, and application checks until steady state.

Example command shape for a reviewed ECS rollback:

```bash
aws ecs update-service \
  --cluster "<cluster>" \
  --service "<service>" \
  --task-definition "<known-good-task-definition-arn>" \
  --region "<aws-region>"
```

Do not copy this command into production without confirming the target account, Region, service, task definition, deployment configuration, and change approval.

### Other deployment targets

For Lambda, S3, CloudFormation, Terraform, or another target, use its approved versioning and rollback mechanism. Keep the same principles:

- restore a known-good immutable version;
- avoid unreviewed manual drift;
- preserve evidence;
- verify the final state independently from the workflow output.

## 6. Verify Recovery

- [ ] Confirm the service has reached its expected steady state.
- [ ] Confirm the running version or digest matches the approved rollback target.
- [ ] Test health checks and one representative user journey.
- [ ] Review error rate, latency, logs, alarms, target health, and deployment events.
- [ ] Confirm no unexpected IAM, networking, secret, or configuration changes remain.
- [ ] Keep monitoring for an agreed observation period before closing the incident.
- [ ] Record who approved the recovery and the evidence used to declare success.

A successful workflow status alone is not proof that the service recovered.

## 7. Prevent Immediate Recurrence

Before re-enabling normal deployment:

- [ ] Identify the direct failure and any contributing control gap.
- [ ] Add or update a pre-deployment check, test, approval, alarm, or rollback step where justified.
- [ ] Confirm immutable release identifiers are retained long enough to support rollback.
- [ ] Confirm production jobs use protected GitHub environments and least-privilege AWS roles.
- [ ] Test the corrected path in a non-production environment.
- [ ] Link the incident, change record, workflow run, release, and follow-up actions.

## Minimum Rollback Record

| Field | Value |
| --- | --- |
| Incident or change reference | `<reference>` |
| Environment and AWS target | `<environment-account-region-service>` |
| Failed workflow run | `<workflow-run-url>` |
| Failed version | `<commit-image-or-release>` |
| Known-good version | `<commit-image-or-release>` |
| Current running version after recovery | `<verified-version>` |
| Decision-maker | `<name-or-role>` |
| Verification evidence | `<dashboards-logs-health-checks>` |
| Follow-up owner and due date | `<owner-yyyy-mm-dd>` |

## Related Repository Guidance

- [Environment protection](environment-protection.md)
- [Troubleshooting](troubleshooting.md)
- [Workflow design](workflow-design.md)
- [Deployment validation checklist](validation-checklist.md)
- [Deployment audit evidence](deployment-audit-evidence.md)
