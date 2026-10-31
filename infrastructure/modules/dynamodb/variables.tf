variable "tables" { type = map(object({ name = string, hash_key = string })) }
variable "billing_mode" { type = string }
variable "enable_pitr" { type = bool }
variable "deletion_protection" { type = bool }
