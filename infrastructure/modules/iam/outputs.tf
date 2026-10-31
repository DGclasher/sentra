output "execution_role_arns" { value = { for key, role in aws_iam_role.execution : key => role.arn } }
output "task_role_arns" { value = { for key, role in aws_iam_role.task : key => role.arn } }
