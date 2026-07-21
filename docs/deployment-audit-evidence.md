# Deployment Audit Evidence

OIDC removes long-lived AWS keys, but deployments still need enough evidence to answer who changed what, when, through which workflow, and with which approval.

## Evidence Sources

### GitHub Actions

Record or retain:

- Repository, workflow name, run ID, run attempt, and commit SHA.
- Triggering actor and event type.
- Referenced environment and any required-reviewer approval.
- Workflow file version and reusable-workflow reference.
- Job conclusion and deployment summary.

Prefer links and stable identifiers over copying complete logs into tickets.

### AWS

Use CloudTrail to confirm:

- `AssumeRoleWithWebIdentity` activity for the deployment role.
- Role session name and source identity available in the event.
- Account, region, timestamp, and principal used for subsequent API calls.
- Material resource changes performed during the deployment window.

Keep CloudTrail enabled, protected, and retained according to the organisation's security and regulatory requirements.

### Deployment Validation

Capture the evidence that proves the release completed safely:

- Terraform plan/apply summary or deployment output.
- Application or infrastructure version deployed.
- Health-check, smoke-test, or synthetic-test result.
- Monitoring links and the observation window.
- Rollback decision and owner.

## Minimal Change-Record Checklist

- [ ] Issue, change, or release identifier.
- [ ] Repository and commit SHA.
- [ ] GitHub workflow run URL and run ID.
- [ ] Triggering actor and approval evidence.
- [ ] Target AWS account, region, environment, and IAM role.
- [ ] CloudTrail event lookup reference or query window.
- [ ] Deployment result and validation evidence.
- [ ] Any exception, failed step, manual intervention, or rollback.
- [ ] Named operational owner for follow-up.

## Safe Retention

- Do not save OIDC tokens, temporary credentials, secret values, or unredacted environment dumps.
- Redact customer data, internal endpoints, account details, and sensitive resource names where the evidence store has a broader audience.
- Store evidence in an access-controlled system with a documented retention period.
- Preserve original GitHub and CloudTrail records rather than relying only on screenshots.
- Test that investigators can correlate the GitHub run ID, role session name, CloudTrail events, and deployed version.

## Incident Use

During an incident, start with the deployment commit and workflow run, identify the assumed-role session in CloudTrail, then trace the AWS API calls made by that session. Record gaps in correlation or retention as control improvements rather than recreating missing evidence manually.
