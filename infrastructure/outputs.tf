output "vpc_id" { value = module.networking.vpc_id }
output "public_subnet_ids" { value = module.networking.public_subnet_ids }
output "private_subnet_ids" { value = module.networking.private_subnet_ids }
output "cognito_user_pool_id" { value = module.cognito.user_pool_id }
output "cognito_user_pool_arn" { value = module.cognito.user_pool_arn }
output "cognito_app_client_id" { value = module.cognito.user_pool_client_id }
output "dynamodb_table_names" { value = module.dynamodb.table_names }
output "dynamodb_table_arns" { value = module.dynamodb.table_arns }
output "ecs_cluster_name" { value = aws_ecs_cluster.this.name }
output "ecs_cluster_arn" { value = aws_ecs_cluster.this.arn }
output "ecs_service_names" { value = { ticket = module.ticket_ecs.service_name, identity = module.identity_ecs.service_name, ai = module.ai_ecs.service_name } }
output "alb_dns_names" { value = { ticket = module.ticket_alb.alb_dns_name, identity = module.identity_alb.alb_dns_name, ai = module.ai_alb.alb_dns_name } }
output "target_group_arns" { value = { ticket = module.ticket_alb.target_group_arn, identity = module.identity_alb.target_group_arn, ai = module.ai_alb.target_group_arn } }
output "api_gateway_id" { value = module.api_gateway.api_id }
output "api_gateway_endpoint" { value = module.api_gateway.api_endpoint }
output "vpc_link_id" { value = module.api_gateway.vpc_link_id }
output "document_bucket_name" { value = aws_s3_bucket.documents.bucket }
output "s3_vector_bucket_name" { value = module.s3_vectors.bucket_name }
output "s3_vector_bucket_arn" { value = module.s3_vectors.bucket_arn }
output "s3_vector_index_name" { value = module.s3_vectors.index_name }
output "s3_vector_index_arn" { value = module.s3_vectors.index_arn }
