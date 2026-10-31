variable "name_prefix" { type = string }
variable "vpc_id" { type = string }
variable "subnet_ids" { type = list(string) }
variable "container_port" {
  type    = number
  default = 8000
}
variable "public_alb" {
  type    = bool
  default = false
}
variable "enable_https" {
  type    = bool
  default = false
}
variable "certificate_arn" {
  type    = string
  default = ""
}
variable "allowed_source_security_group_ids" {
  type    = list(string)
  default = []
}
variable "health_check" { type = object({ interval = number, timeout = number, healthy_threshold = number, unhealthy_threshold = number }) }
