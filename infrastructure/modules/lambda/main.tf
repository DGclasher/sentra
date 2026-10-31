data "archive_file" "package" {
  type        = "zip"
  source_file = var.source_file
  output_path = "${path.root}/.terraform/${var.function_name}.zip"
}

resource "aws_iam_role" "this" {
  name               = "${var.name_prefix}-pre-signup-role"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "lambda.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}

resource "aws_iam_role_policy" "this" {
  role = aws_iam_role.this.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [
    { Effect = "Allow", Action = ["dynamodb:PutItem"], Resource = var.users_table_arn },
    { Effect = "Allow", Action = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"], Resource = "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.function_name}:*" }
  ] })
}

resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  role             = aws_iam_role.this.arn
  handler          = "lambda_function.lambda_handler"
  runtime          = var.runtime
  architectures    = [var.architecture]
  filename         = data.archive_file.package.output_path
  source_code_hash = data.archive_file.package.output_base64sha256
  environment { variables = { USERS_TABLE_NAME = var.users_table_name } }
}
