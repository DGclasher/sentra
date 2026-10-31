resource "aws_security_group" "task" {
  name        = "${var.name_prefix}-task-sg"
  description = "ECS task traffic from the service ALB"
  vpc_id      = var.vpc_id
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [var.alb_security_group_id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "${var.name_prefix}-task-sg" }
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/ecs/${var.name_prefix}"
  retention_in_days = var.log_retention_days
  tags              = { Name = "/ecs/${var.name_prefix}" }
}

resource "aws_ecs_task_definition" "this" {
  family                   = var.name_prefix
  cpu                      = var.cpu
  memory                   = var.memory
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  container_definitions = jsonencode([{
    name                  = var.container_name
    image                 = var.image
    essential             = true
    portMappings          = [{ containerPort = var.container_port, hostPort = var.container_port, protocol = "tcp" }]
    environment           = [for key, value in var.environment : { name = key, value = value }]
    secrets               = [for key, value in var.secrets : { name = key, valueFrom = value }]
    repositoryCredentials = var.repository_credentials_secret_arn != "" ? { credentialsParameter = var.repository_credentials_secret_arn } : null
    healthCheck           = { command = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/health || exit 1"], interval = 30, timeout = 10, retries = 3, startPeriod = 5 }
    logConfiguration      = { logDriver = "awslogs", options = { awslogs-group = aws_cloudwatch_log_group.this.name, awslogs-region = var.aws_region, awslogs-stream-prefix = var.container_name } }
  }])
}

resource "aws_ecs_service" "this" {
  name             = var.name_prefix
  cluster          = var.cluster_arn
  task_definition  = aws_ecs_task_definition.this.arn
  desired_count    = var.desired_count
  launch_type      = "FARGATE"
  platform_version = "LATEST"
  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.task.id]
    assign_public_ip = false
  }
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.container_name
    container_port   = var.container_port
  }
  depends_on = [aws_cloudwatch_log_group.this]
}
