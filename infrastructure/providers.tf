provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.tags
  }
}

provider "awscc" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}
