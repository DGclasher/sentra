variable "user_pool_name" { type = string }
variable "pre_signup_lambda_arn" { type = string }
variable "callback_urls" { type = list(string) }
variable "logout_urls" { type = list(string) }
