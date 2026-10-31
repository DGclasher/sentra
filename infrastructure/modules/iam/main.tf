locals {
  task_permissions = {
    ticket = {
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Scan", "dynamodb:DeleteItem", "dynamodb:UpdateItem"]
      resources = [var.table_arns.users, var.table_arns.staffs, var.table_arns.tickets, var.table_arns.messages]
    }
    identity = {
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:Scan", "dynamodb:DeleteItem", "dynamodb:UpdateItem", "cognito-idp:AdminCreateUser", "cognito-idp:AdminGetUser", "cognito-idp:AdminUpdateUserAttributes", "cognito-idp:AdminDeleteUser", "cognito-idp:ListUsers"]
      resources = concat([var.table_arns.users, var.table_arns.staffs], [var.cognito_user_pool_arn])
    }
    ai = {
      actions   = ["dynamodb:GetItem", "dynamodb:Scan", "s3:PutObject", "s3vectors:PutVectors", "s3vectors:QueryVectors"]
      resources = concat([var.table_arns.users, var.table_arns.staffs, var.document_bucket_arn], [var.s3_vector_bucket_arn, var.s3_vector_index_arn])
    }
  }
}

resource "aws_iam_role" "execution" {
  for_each           = toset(["ticket", "identity", "ai"])
  name               = "${var.name_prefix}-${each.key}-execution"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}

resource "aws_iam_role_policy" "execution" {
  for_each = aws_iam_role.execution
  role     = each.value.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = concat(
      [{ Effect = "Allow", Action = ["logs:CreateLogStream", "logs:PutLogEvents"], Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/ecs/${var.name_prefix}-${each.key}:*" }],
      length(var.secret_arns) > 0 ? [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = var.secret_arns }] : []
    )
  })
}

resource "aws_iam_role" "task" {
  for_each           = toset(["ticket", "identity", "ai"])
  name               = "${var.name_prefix}-${each.key}-task"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}

resource "aws_iam_role_policy" "task" {
  for_each = aws_iam_role.task
  role     = each.value.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = local.task_permissions[each.key].actions, Resource = local.task_permissions[each.key].resources }
  ] })
}
