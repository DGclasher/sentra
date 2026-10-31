variable "name_prefix" { type = string }
variable "aws_region" { type = string }
variable "table_arns" { type = object({ users = string, staffs = string, tickets = string, messages = string }) }
variable "cognito_user_pool_arn" { type = string }
variable "document_bucket_arn" { type = string }
variable "s3_vector_bucket_arn" { type = string }
variable "s3_vector_index_arn" { type = string }
variable "secret_arns" {
  type    = list(string)
  default = []
}
