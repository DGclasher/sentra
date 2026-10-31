module "networking" {
  source               = "./modules/networking"
  name_prefix          = local.name_prefix
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  enable_nat_gateway   = var.enable_nat_gateway
  single_nat_gateway   = var.single_nat_gateway
}

module "dynamodb" {
  source              = "./modules/dynamodb"
  billing_mode        = var.billing_mode
  enable_pitr         = var.enable_dynamodb_pitr
  deletion_protection = var.enable_dynamodb_deletion_protection
  tables = {
    users    = { name = local.table_names.users, hash_key = "userId" }
    staffs   = { name = local.table_names.staffs, hash_key = "staffId" }
    tickets  = { name = local.table_names.tickets, hash_key = "ticketId" }
    messages = { name = local.table_names.messages, hash_key = "messageId" }
  }
}

module "pre_signup_lambda" {
  source           = "./modules/lambda"
  name_prefix      = local.name_prefix
  function_name    = "${local.name_prefix}-pre-signup"
  source_file      = "${path.root}/lambda/pre_signup/lambda_function.py"
  runtime          = var.lambda_runtime
  architecture     = var.lambda_architecture
  aws_region       = var.aws_region
  users_table_name = module.dynamodb.table_names.users
  users_table_arn  = module.dynamodb.table_arns.users
}

module "cognito" {
  source                = "./modules/cognito"
  user_pool_name        = "${local.name_prefix}-user-pool"
  pre_signup_lambda_arn = module.pre_signup_lambda.function_arn
  callback_urls         = var.cognito_callback_urls
  logout_urls           = var.cognito_logout_urls
}

module "s3_vectors" {
  source = "./modules/s3-vectors"

  providers = {
    awscc = awscc
  }

  bucket_name  = var.s3_vector_bucket_name
  index_name   = var.s3_vector_index_name
  dimension    = var.s3_vector_dimension
  project_name = var.project_name
  environment  = var.environment
}

resource "aws_s3_bucket" "documents" {
  bucket        = var.s3_doc_storage_bucket_name != "" ? var.s3_doc_storage_bucket_name : "${local.name_prefix}-ai-documents"
  force_destroy = false
  tags          = { Name = "${local.name_prefix}-ai-documents" }
}

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket                  = aws_s3_bucket.documents.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule { object_ownership = "BucketOwnerEnforced" }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_secretsmanager_secret" "groq" {
  count                   = var.groq_api_key != "" ? 1 : 0
  name                    = "${local.name_prefix}/groq-api-key-v2"
  recovery_window_in_days = 7
}

resource "aws_secretsmanager_secret_version" "groq" {
  count         = var.groq_api_key != "" ? 1 : 0
  secret_id     = aws_secretsmanager_secret.groq[0].id
  secret_string = var.groq_api_key
}

resource "aws_security_group" "vpc_link" {
  name        = "${local.name_prefix}-api-vpc-link-sg"
  description = "API Gateway VPC Link egress"
  vpc_id      = module.networking.vpc_id
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${local.name_prefix}-api-vpc-link-sg" }
}

module "ticket_alb" {
  source                            = "./modules/alb"
  name_prefix                       = local.service_names.ticket
  vpc_id                            = module.networking.vpc_id
  subnet_ids                        = var.public_albs ? module.networking.public_subnet_ids : module.networking.private_subnet_ids
  public_alb                        = var.public_albs
  enable_https                      = var.enable_https
  certificate_arn                   = var.acm_certificate_arn
  allowed_source_security_group_ids = [aws_security_group.vpc_link.id]
  health_check                      = var.target_health_check
}

module "identity_alb" {
  source                            = "./modules/alb"
  name_prefix                       = local.service_names.identity
  vpc_id                            = module.networking.vpc_id
  subnet_ids                        = var.public_albs ? module.networking.public_subnet_ids : module.networking.private_subnet_ids
  public_alb                        = var.public_albs
  enable_https                      = var.enable_https
  certificate_arn                   = var.acm_certificate_arn
  allowed_source_security_group_ids = [aws_security_group.vpc_link.id]
  health_check                      = var.target_health_check
}

module "ai_alb" {
  source                            = "./modules/alb"
  name_prefix                       = local.service_names.ai
  vpc_id                            = module.networking.vpc_id
  subnet_ids                        = var.public_albs ? module.networking.public_subnet_ids : module.networking.private_subnet_ids
  public_alb                        = var.public_albs
  enable_https                      = var.enable_https
  certificate_arn                   = var.acm_certificate_arn
  allowed_source_security_group_ids = [aws_security_group.vpc_link.id]
  health_check                      = var.target_health_check
}

module "iam" {
  source                = "./modules/iam"
  name_prefix           = local.name_prefix
  aws_region            = var.aws_region
  table_arns            = module.dynamodb.table_arns
  cognito_user_pool_arn = module.cognito.user_pool_arn
  document_bucket_arn   = "${aws_s3_bucket.documents.arn}/*"
  s3_vector_bucket_arn  = module.s3_vectors.bucket_arn
  s3_vector_index_arn   = module.s3_vectors.index_arn
  secret_arns           = compact(concat(var.dockerhub_credentials_secret_arn != "" ? [var.dockerhub_credentials_secret_arn] : [], length(aws_secretsmanager_secret.groq) > 0 ? [aws_secretsmanager_secret.groq[0].arn] : []))
}

resource "aws_ecs_cluster" "this" {
  name = "${local.name_prefix}-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = { Name = "${local.name_prefix}-cluster" }
}

module "ticket_ecs" {
  source                            = "./modules/ecs"
  name_prefix                       = local.service_names.ticket
  container_name                    = "sentra-ticket-service"
  image                             = var.ticket_service_image
  vpc_id                            = module.networking.vpc_id
  private_subnet_ids                = module.networking.private_subnet_ids
  alb_security_group_id             = module.ticket_alb.alb_security_group_id
  target_group_arn                  = module.ticket_alb.target_group_arn
  cluster_arn                       = aws_ecs_cluster.this.arn
  execution_role_arn                = module.iam.execution_role_arns.ticket
  task_role_arn                     = module.iam.task_role_arns.ticket
  aws_region                        = var.aws_region
  cpu                               = var.ticket_service_cpu
  memory                            = var.ticket_service_memory
  desired_count                     = var.ecs_desired_count
  environment                       = { AWS_REGION = var.aws_region, USERS_TABLE_NAME = module.dynamodb.table_names.users, STAFFS_TABLE_NAME = module.dynamodb.table_names.staffs, TICKETS_TABLE_NAME = module.dynamodb.table_names.tickets, MESSAGES_TABLE_NAME = module.dynamodb.table_names.messages }
  repository_credentials_secret_arn = var.dockerhub_credentials_secret_arn
}

module "identity_ecs" {
  source                            = "./modules/ecs"
  name_prefix                       = local.service_names.identity
  container_name                    = "sentra-identity-service"
  image                             = var.identity_service_image
  vpc_id                            = module.networking.vpc_id
  private_subnet_ids                = module.networking.private_subnet_ids
  alb_security_group_id             = module.identity_alb.alb_security_group_id
  target_group_arn                  = module.identity_alb.target_group_arn
  cluster_arn                       = aws_ecs_cluster.this.arn
  execution_role_arn                = module.iam.execution_role_arns.identity
  task_role_arn                     = module.iam.task_role_arns.identity
  aws_region                        = var.aws_region
  cpu                               = var.identity_service_cpu
  memory                            = var.identity_service_memory
  desired_count                     = var.ecs_desired_count
  environment                       = { AWS_REGION = var.aws_region, COGNITO_USER_POOL_ID = module.cognito.user_pool_id, COGNITO_CLIENT_ID = module.cognito.user_pool_client_id, USERS_TABLE_NAME = module.dynamodb.table_names.users, STAFFS_TABLE_NAME = module.dynamodb.table_names.staffs, DYNAMODB_USER_TABLE_NAME = module.dynamodb.table_names.users, DYNAMODB_STAFF_TABLE_NAME = module.dynamodb.table_names.staffs }
  repository_credentials_secret_arn = var.dockerhub_credentials_secret_arn
}

module "ai_ecs" {
  source                            = "./modules/ecs"
  name_prefix                       = local.service_names.ai
  container_name                    = "sentra-ai-service"
  image                             = var.ai_service_image
  vpc_id                            = module.networking.vpc_id
  private_subnet_ids                = module.networking.private_subnet_ids
  alb_security_group_id             = module.ai_alb.alb_security_group_id
  target_group_arn                  = module.ai_alb.target_group_arn
  cluster_arn                       = aws_ecs_cluster.this.arn
  execution_role_arn                = module.iam.execution_role_arns.ai
  task_role_arn                     = module.iam.task_role_arns.ai
  aws_region                        = var.aws_region
  cpu                               = var.ai_service_cpu
  memory                            = var.ai_service_memory
  desired_count                     = var.ecs_desired_count
  environment                       = { AWS_REGION = var.aws_region, S3_BUCKET_NAME = var.s3_vector_bucket_name, S3_BUCKET_INDEX = var.s3_vector_index_name, S3_DOC_STORAGE_BUCKET_NAME = aws_s3_bucket.documents.bucket, EMBEDDING_MODEL = var.embedding_model, STAFF_TABLE_NAME = module.dynamodb.table_names.staffs, STAFFS_TABLE_NAME = module.dynamodb.table_names.staffs, USERS_TABLE_NAME = module.dynamodb.table_names.users, TICKET_SERVICE_URL = "http://${module.ticket_alb.alb_dns_name}" }
  secrets                           = length(aws_secretsmanager_secret.groq) > 0 ? { GROQ_API_KEY = aws_secretsmanager_secret.groq[0].arn } : {}
  repository_credentials_secret_arn = var.dockerhub_credentials_secret_arn
}

module "api_gateway" {
  source                     = "./modules/api-gateway"
  name_prefix                = "${local.name_prefix}-api"
  aws_region                 = var.aws_region
  private_subnet_ids         = module.networking.private_subnet_ids
  vpc_link_security_group_id = aws_security_group.vpc_link.id
  ticket_listener_arn        = module.ticket_alb.listener_arn
  identity_listener_arn      = module.identity_alb.listener_arn
  ai_listener_arn            = module.ai_alb.listener_arn
  user_pool_id               = module.cognito.user_pool_id
  user_pool_client_id        = module.cognito.user_pool_client_id
  issuer_url                 = module.cognito.issuer_url
  stage_name                 = var.api_gateway_stage_name
}
