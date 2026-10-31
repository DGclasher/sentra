locals {
  name_prefix = "${var.project_name}-${var.environment}"

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  service_names = {
    ticket   = "${local.name_prefix}-ticket"
    ai       = "${local.name_prefix}-ai"
    identity = "${local.name_prefix}-identity"
  }

  table_names = {
    users    = "${local.name_prefix}-users"
    staffs   = "${local.name_prefix}-staffs"
    tickets  = "${local.name_prefix}-tickets"
    messages = "${local.name_prefix}-messages"
  }
}
