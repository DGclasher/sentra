variable "name_prefix" { type = string }
variable "container_name" { type = string }
variable "image" { type = string }
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "alb_security_group_id" { type = string }
variable "target_group_arn" { type = string }
variable "cluster_arn" { type = string }
variable "execution_role_arn" { type = string }
variable "task_role_arn" { type = string }
variable "aws_region" { type = string }
variable "cpu" { type = number }
variable "memory" { type = number }
variable "desired_count" { type = number }
variable "container_port" {
  type    = number
  default = 8000
}
variable "environment" {
  type    = map(string)
  default = {}
}
variable "secrets" {
  type    = map(string)
  default = {}
}
variable "repository_credentials_secret_arn" {
  type    = string
  default = ""
}
variable "log_retention_days" {
  type    = number
  default = 30
}
