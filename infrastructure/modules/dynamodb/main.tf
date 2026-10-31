resource "aws_dynamodb_table" "this" {
  for_each     = var.tables
  name         = each.value.name
  billing_mode = var.billing_mode
  hash_key     = each.value.hash_key
  attribute {
    name = each.value.hash_key
    type = "S"
  }
  point_in_time_recovery { enabled = var.enable_pitr }
  deletion_protection_enabled = var.deletion_protection
  server_side_encryption { enabled = true }
  tags = { Name = each.value.name }
}
