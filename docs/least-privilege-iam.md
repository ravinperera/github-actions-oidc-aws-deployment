# Least-Privilege IAM for GitHub Actions OIDC

OIDC controls who can request temporary AWS credentials. Least-privilege IAM controls what those temporary credentials can do after the role is assumed.

Treat both layers as required. A narrow trust policy with an overly broad permissions policy can still create production risk.

## Design Principles

1. Use one deployment role per environment.
2. Scope permissions to the services the workflow actually deploys.
3. Scope resources to known ARNs where practical.
4. Use IAM conditions for region, tags, or resource paths where they add meaningful control.
5. Review policies whenever the workflow starts deploying a new service or resource type.

## Permission Scoping Checklist

For each workflow job, confirm:

- which AWS services are touched;
- which actions are required for plan, deploy, and rollback;
- whether read-only permissions can be separated from write permissions;
- whether production requires a separate role from dev and staging;
- whether resource ARNs can replace `*`;
- whether conditions such as `aws:RequestedRegion` or resource tags can be used.

## Safer Policy Shape

Prefer policies that are explicit and grouped by deployment responsibility.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReadDeploymentState",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::example-terraform-state",
        "arn:aws:s3:::example-terraform-state/*"
      ]
    },
    {
      "Sid": "AllowDeploymentInApprovedRegion",
      "Effect": "Allow",
      "Action": [
        "cloudformation:CreateChangeSet",
        "cloudformation:ExecuteChangeSet",
        "cloudformation:Describe*"
      ],
      "Resource": "arn:aws:cloudformation:eu-west-2:123456789012:stack/example-*/*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "eu-west-2"
        }
      }
    }
  ]
}
```

## Patterns to Avoid

Avoid using these in production deployment roles unless there is a clear, reviewed exception:

```json
{
  "Effect": "Allow",
  "Action": "*",
  "Resource": "*"
}
```

```json
{
  "Effect": "Allow",
  "Action": "iam:*",
  "Resource": "*"
}
```

```json
{
  "Effect": "Allow",
  "Action": [
    "sts:AssumeRole",
    "iam:PassRole"
  ],
  "Resource": "*"
}
```

These patterns make it difficult to prove what the workflow can change and can allow unintended privilege escalation.

## Deny Guardrails

For sensitive environments, consider explicit deny statements or organization-level controls for:

- actions outside approved AWS regions;
- changes to identity, billing, or organization-level services;
- disabling logging or security services;
- deleting production backup or state resources.

Use deny guardrails carefully. They are powerful, but they should be tested in lower environments first to avoid blocking legitimate deployments.

## Review Cadence

Review deployment role policies when:

- a workflow adds a new AWS service;
- a deployment moves from dev to staging or production;
- Terraform modules or deployment tooling change;
- an incident, failed deployment, or near miss exposes an access gap;
- a quarterly access review is performed.

Keep the IAM policy close to the workflow documentation so reviewers can understand why each permission exists.
