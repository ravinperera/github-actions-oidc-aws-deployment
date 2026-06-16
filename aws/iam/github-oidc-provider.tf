terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_iam_openid_connect_provider" "github" {
  url = "https://token.actions.githubusercontent.com"

  client_id_list = [
    "sts.amazonaws.com"
  ]

  # Example thumbprint. Validate current AWS/GitHub guidance before production use.
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1"
  ]

  tags = var.tags
}

variable "aws_region" {
  description = "AWS region used by the provider."
  type        = string
  default     = "eu-west-2"
}

variable "tags" {
  description = "Tags applied to supported resources."
  type        = map(string)
  default     = {}
}

output "github_oidc_provider_arn" {
  description = "GitHub OIDC provider ARN."
  value       = aws_iam_openid_connect_provider.github.arn
}
