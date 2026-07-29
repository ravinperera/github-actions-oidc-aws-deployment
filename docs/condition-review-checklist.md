# OIDC Identity Condition Review Checklist

Use this checklist before allowing a GitHub Actions workflow to assume an AWS IAM role. It focuses on the identity conditions in the role trust policy, not the permissions granted after the role is assumed.

Replace every placeholder with reviewed values from your own GitHub and AWS configuration.

## 1. Audience

- [ ] Confirm `token.actions.githubusercontent.com:aud` is present.
- [ ] For the standard AWS credential action, confirm the value is exactly `sts.amazonaws.com`.
- [ ] Use `StringEquals` unless a documented integration requires a different audience pattern.
- [ ] Reject a trust policy that checks only the audience and does not restrict the subject.

Safe example:

```json
"StringEquals": {
  "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
}
```

Risky example:

```json
"StringLike": {
  "token.actions.githubusercontent.com:aud": "*"
}
```

## 2. Repository Owner And Repository

- [ ] Restrict the trust policy to the intended GitHub owner and repository.
- [ ] Confirm spelling and case against the actual repository path.
- [ ] Use the immutable `repository_id` or `repository_owner_id` claim as an additional control where the organisation's tooling supports and validates it.
- [ ] Do not allow every repository in an organisation unless the role is deliberately designed for that scope.
- [ ] Do not share a production deployment role across unrelated repositories.

Safe subject prefix:

```text
repo:<github-owner>/<repository>:
```

Risky subject pattern:

```text
repo:<github-owner>/*
```

## 3. Branch Or Tag Conditions

Use a branch or tag subject only when the job does not reference a GitHub environment.

- [ ] Restrict branch deployments to the exact reviewed branch where practical.
- [ ] Use the full ref form, such as `refs/heads/<branch>` or `refs/tags/<tag>`.
- [ ] Confirm the workflow trigger cannot be reached from an untrusted branch.
- [ ] Avoid broad wildcards such as every branch or every tag for a production role.
- [ ] If release tags are permitted, document who can create or move those tags.

Safe branch subject:

```text
repo:<github-owner>/<repository>:ref:refs/heads/<branch>
```

Safe release-tag pattern when formally controlled:

```text
repo:<github-owner>/<repository>:ref:refs/tags/v*
```

Risky subject pattern:

```text
repo:<github-owner>/<repository>:*
```

## 4. GitHub Environment Conditions

When a job references a GitHub environment, the default subject contains the environment name rather than the branch ref.

- [ ] Confirm the trust policy expects `environment:<environment>` for environment-based jobs.
- [ ] Configure deployment branch or tag restrictions on the GitHub environment.
- [ ] Require independent reviewers for production environments where the repository plan supports them.
- [ ] Restrict who can modify the environment, its secrets, variables, and protection rules.
- [ ] Confirm the workflow cannot select an arbitrary environment name from untrusted input.

Safe environment subject:

```text
repo:<github-owner>/<repository>:environment:<environment>
```

Risky configuration:

```text
A production role trusts an environment subject, but the GitHub environment has no branch restrictions or approval protection.
```

## 5. Pull Request Workflows

- [ ] Do not let a pull request workflow assume a production deployment role.
- [ ] Treat workflows triggered from forks as untrusted unless there is a narrowly reviewed design.
- [ ] If a read-only validation role is required for pull requests, use a separate role with minimal permissions and a pull-request-specific subject.
- [ ] Do not expose environment secrets or write-capable cloud permissions to untrusted pull request code.

Pull-request subject shape:

```text
repo:<github-owner>/<repository>:pull_request
```

## 6. Workflow And Ref Defence In Depth

AWS supports additional GitHub OIDC claims as condition keys. Use them only after confirming that the selected claims are present and stable for the workflow path.

- [ ] Consider restricting `workflow`, `job_workflow_ref`, `ref`, `environment`, `repository_id`, or `repository_owner_id` as defence in depth.
- [ ] Prefer immutable identifiers where repository renames or ownership changes are a material risk.
- [ ] Keep conditions understandable enough that responders can diagnose failures safely.
- [ ] Test the final condition set from the intended branch, tag, or environment before production use.

## 7. Complete Trust Condition Example

This example allows one repository and one branch to request credentials. It grants no AWS resource permissions by itself.

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:<github-owner>/<repository>:ref:refs/heads/<branch>"
    }
  }
}
```

For an environment-based deployment, replace the subject with:

```text
repo:<github-owner>/<repository>:environment:<environment>
```

## 8. Review Record

Record the decision before enabling the role:

| Item | Reviewed value |
| --- | --- |
| GitHub owner | `<github-owner>` |
| Repository | `<repository>` |
| Repository ID, if used | `<repository-id>` |
| Allowed branch, tag, or environment | `<approved-source>` |
| Audience | `sts.amazonaws.com` |
| AWS account and role | `<aws-account-id>` / `<role-name>` |
| GitHub environment protections | `<reviewers-and-branch-rules>` |
| Reviewer | `<reviewer>` |
| Review date | `<yyyy-mm-dd>` |
| Next review or trigger | `<date-or-change-trigger>` |

Re-run this review after repository transfers or renames, workflow trigger changes, environment protection changes, trust policy changes, or deployment-role scope changes.

## Official References

- [GitHub OpenID Connect reference](https://docs.github.com/en/actions/reference/security/oidc)
- [GitHub: Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/how-tos/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM: Configuring a role for the GitHub OIDC identity provider](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-idp_oidc.html)
- [AWS IAM and STS condition context keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_iam-condition-keys.html)
