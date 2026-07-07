# OIDC Deployment Validation Checklist

Use this checklist before treating a GitHub Actions OIDC deployment path as production-ready. It is designed for reviewers who need to confirm that GitHub, AWS IAM, and operational controls line up.

## GitHub Workflow Checks

- [ ] The workflow uses `permissions: id-token: write` only for jobs that need AWS credentials.
- [ ] The workflow uses `permissions: contents: read` unless write access is genuinely required.
- [ ] Production deployment jobs are tied to a GitHub Environment.
- [ ] Production jobs do not run automatically from arbitrary feature branches.
- [ ] Workflow dispatch inputs are constrained and easy to review.
- [ ] The workflow logs the target environment and role name without exposing sensitive values.

## GitHub Environment Checks

- [ ] Production has required reviewers configured.
- [ ] Production has branch or tag restrictions configured.
- [ ] Environment variables are separated by environment.
- [ ] Static AWS access keys are not stored as repository or environment secrets.
- [ ] Deployment history can be reviewed from the environment page.

## AWS OIDC Provider Checks

- [ ] The AWS account has one GitHub OIDC provider configured for `token.actions.githubusercontent.com`.
- [ ] The provider audience is set to `sts.amazonaws.com`.
- [ ] Provider setup is managed as code or recorded as evidence.
- [ ] The provider is not duplicated unnecessarily across the same AWS account.

## IAM Trust Policy Checks

- [ ] The trust policy restricts the GitHub organization or repository.
- [ ] Production role trust policy restricts the expected branch, tag, or environment claim.
- [ ] Wildcards are avoided for production role assumptions.
- [ ] The role session duration is appropriate for the workflow.
- [ ] Role names clearly identify the target environment.

## IAM Permissions Checks

- [ ] Each environment has a separate deployment role.
- [ ] Production permissions are narrower than or equal to lower-environment permissions.
- [ ] `Action: "*"` is not used for production deployment roles.
- [ ] `Resource: "*"` is justified where AWS does not support resource-level permissions.
- [ ] `iam:PassRole` is scoped to known deployment roles.
- [ ] Region or tag conditions are used where practical.

## Operational Evidence

Keep evidence for:

- successful workflow run URL;
- AWS role assumed by the workflow;
- Terraform plan or deployment output;
- approval record for production deployments;
- rollback or backout decision;
- date of IAM policy review.

## Red Flags That Should Block Production Rollout

Do not promote the workflow to production if any of these are true:

- static AWS access keys are still used as a fallback;
- feature branches can assume the production role;
- the production role has broad administrator permissions;
- no one reviews production deployments;
- deployment logs do not show which environment was targeted;
- rollback steps are unknown or untested.

## Review Outcome

A deployment path is ready when the workflow, GitHub Environment, AWS trust policy, and IAM permissions all describe the same intended release path. If one layer is broader than the others, fix that layer before production use.
