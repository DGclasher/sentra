variable "name_prefix" { type = string }
variable "aws_region" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "vpc_link_security_group_id" { type = string }
variable "ticket_listener_arn" { type = string }
variable "identity_listener_arn" { type = string }
variable "ai_listener_arn" { type = string }
variable "user_pool_id" { type = string }
variable "user_pool_client_id" { type = string }
variable "issuer_url" { type = string }
variable "stage_name" {
  type    = string
  default = "$default"
}
