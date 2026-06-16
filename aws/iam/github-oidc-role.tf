data "aws_iam_policy_document" "github_actions_assume_role" {
  statement {
    effect = "Allow"

    actions = [
      "sts:AssumeRoleWithWebIdentity"
    ]

    principals {
      type = "Federated"
      identifiers = [
        var.github_oidc_provider_arn
      ]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values = [
        "repo:${var.github_owner}/${var.github_repository}:ref:refs/heads/${var.allowed_branch}",
        "repo:${var.github_owner}/${var.github_repository}:environment:${var.github_environment}"
      ]
    }
  }
}

resource "aws_iam_role" "github_actions_deploy" {
  name               = "${var.project_name}-${var.environment}-github-actions-role"
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role.json
  tags               = var.tags
}

resource "aws_iam_role_policy" "deployment" {
  name   = "${var.project_name}-${var.environment}-deployment-policy"
  role   = aws_iam_role.github_actions_deploy.id
  policy = file("${path.module}/deployment-policy.json")
}

variable "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider."
  type        = string
}

variable "github_owner" {
  description = "GitHub user or organisation."
  type        = string
  default     = "ravinperera"
}

variable "github_repository" {
  description = "GitHub repository allowed to assume this role."
  type        = string
  default     = "github-actions-oidc-aws-deployment"
}

variable "allowed_branch" {
  description = "Branch allowed to assume this role."
  type        = string
  default     = "main"
}

variable "github_environment" {
  description = "GitHub environment allowed to assume this role."
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project name used for IAM role naming."
  type        = string
  default     = "example-app"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "prod"
}

output "github_actions_role_arn" {
  description = "IAM role ARN for GitHub Actions deployments."
  value       = aws_iam_role.github_actions_deploy.arn
}
