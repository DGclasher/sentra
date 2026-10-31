terraform {
  required_providers {
    awscc = {
      source                = "hashicorp/awscc"
      configuration_aliases = [awscc]
    }
  }

  required_version = ">= 1.6.0"
}
