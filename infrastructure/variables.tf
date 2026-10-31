variable "project_name" {
  type    = string
  default = "sentra"
}
variable "environment" {
  type    = string
  default = "production"
}
variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "vpc_cidr" { type = string }
variable "public_subnet_cidrs" { type = list(string) }
variable "private_subnet_cidrs" { type = list(string) }
variable "availability_zones" {
  type    = list(string)
  default = []
}
variable "enable_nat_gateway" {
  type    = bool
  default = true
}
variable "single_nat_gateway" {
  type    = bool
  default = false
}
variable "public_albs" {
  type    = bool
  default = false
}
variable "enable_https" {
  type    = bool
  default = false
}
variable "acm_certificate_arn" {
  type    = string
  default = ""
}
variable "api_gateway_stage_name" {
  type    = string
  default = "$default"
}
variable "cognito_callback_urls" { type = list(string) }
variable "cognito_logout_urls" { type = list(string) }
variable "billing_mode" {
  type    = string
  default = "PAY_PER_REQUEST"
}
variable "enable_dynamodb_pitr" {
  type    = bool
  default = true
}
variable "enable_dynamodb_deletion_protection" {
  type    = bool
  default = true
}
variable "lambda_runtime" {
  type    = string
  default = "python3.12"
}
variable "lambda_architecture" {
  type    = string
  default = "arm64"
}
variable "ecs_desired_count" {
  type    = number
  default = 1
}
variable "ecs_cpu" {
  type    = number
  default = 256
}
variable "ecs_memory" {
  type    = number
  default = 512
}
variable "ticket_service_cpu" {
  type    = number
  default = 256
}
variable "ticket_service_memory" {
  type    = number
  default = 512
}
variable "ai_service_cpu" {
  type    = number
  default = 512
}
variable "ai_service_memory" {
  type    = number
  default = 2048
}
variable "identity_service_cpu" {
  type    = number
  default = 256
}
variable "identity_service_memory" {
  type    = number
  default = 512
}
variable "ticket_service_image" { type = string }
variable "ai_service_image" { type = string }
variable "identity_service_image" { type = string }
variable "dockerhub_credentials_secret_arn" {
  type    = string
  default = ""
}
variable "groq_api_key" {
  type      = string
  sensitive = true
  default   = ""
}
variable "embedding_model" {
  type    = string
  default = "sentence-transformers/all-MiniLM-L12-v2"
}
variable "s3_doc_storage_bucket_name" {
  type    = string
  default = "sentra-ai-doc-bucket"
}
variable "s3_vector_bucket_name" {
  type    = string
  default = "sentra-ai-bucket"
}
variable "s3_vector_index_name" {
  type    = string
  default = "sentra-ai-bucket-index"
}
variable "s3_vector_dimension" {
  type    = number
  default = 384
}
variable "target_health_check" {
  type    = object({ interval = number, timeout = number, healthy_threshold = number, unhealthy_threshold = number })
  default = { interval = 30, timeout = 5, healthy_threshold = 2, unhealthy_threshold = 3 }
}
