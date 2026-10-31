# Sentra AWS infrastructure

This directory contains Terraform for the Sentra VPC, Cognito, DynamoDB, ECS/Fargate services, ALBs, and API Gateway HTTP API. The default topology keeps ECS tasks and internal ALBs private and exposes them through API Gateway VPC Link.

## Validate

```sh
terraform fmt -recursive
terraform init -backend=false
terraform validate
```

These commands are static/configuration validation only. Do not run `terraform apply` from this task.

## Deploy manually

After reviewing the generated plan and configuring a local, untracked `terraform.tfvars`:

```sh
terraform init
terraform plan
terraform apply
```

## Important inputs

The services use port `8000` and `/health`. Ticket and identity use DynamoDB tables created here. AI uses the Terraform-managed S3 Vectors bucket `sentra-ai-bucket` and index `sentra-ai-bucket-index` with 384-dimensional float32 vectors by default. AI uploads PDFs to the separate S3 bucket `sentra-ai-doc-bucket`.

`groq_api_key` is stored in Secrets Manager and injected into the AI task through ECS secrets. Docker Hub private-image authentication is supported by passing an existing Secrets Manager secret ARN in `dockerhub_credentials_secret_arn`.
