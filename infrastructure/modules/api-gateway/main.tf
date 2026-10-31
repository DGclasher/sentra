resource "aws_apigatewayv2_api" "this" {
  name          = var.name_prefix
  protocol_type = "HTTP"
  description   = "Sentra private HTTP API"
}

resource "aws_apigatewayv2_vpc_link" "this" {
  name               = "${var.name_prefix}-vpc-link"
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [var.vpc_link_security_group_id]
}

resource "aws_apigatewayv2_authorizer" "jwt" {
  api_id           = aws_apigatewayv2_api.this.id
  authorizer_type  = "JWT"
  authorizer_uri   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${var.user_pool_id}"
  identity_sources = ["$request.header.Authorization"]
  name             = "${var.name_prefix}-cognito-jwt"
  jwt_configuration {
    audience = [var.user_pool_client_id]
    issuer   = var.issuer_url
  }
}

locals {
  services = {
    ticket   = { prefix = "/api/v1/tickets", listener_arn = var.ticket_listener_arn }
    identity = { prefix = "/api/v1/identity", listener_arn = var.identity_listener_arn }
    ai       = { prefix = "/api/v1/ai", listener_arn = var.ai_listener_arn }
  }
  route_specs = merge(flatten([for key, service in local.services : {
    "${key}-base"  = { route_key = "ANY ${service.prefix}", listener_arn = service.listener_arn, path = service.prefix }
    "${key}-proxy" = { route_key = "ANY ${service.prefix}/{proxy+}", listener_arn = service.listener_arn, path = "${service.prefix}/$request.path.proxy" }
  }])...)
}

resource "aws_apigatewayv2_integration" "service" {
  for_each           = local.route_specs
  api_id             = aws_apigatewayv2_api.this.id
  integration_type   = "HTTP_PROXY"
  integration_method = "ANY"
  integration_uri    = each.value.listener_arn
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.this.id
  request_parameters = {
    "overwrite:path"             = each.value.path
    "overwrite:header.X-User-Id" = "$context.authorizer.claims.sub"
  }
}

resource "aws_apigatewayv2_route" "service" {
  for_each           = local.route_specs
  api_id             = aws_apigatewayv2_api.this.id
  route_key          = each.value.route_key
  target             = "integrations/${aws_apigatewayv2_integration.service[each.key].id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt.id
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.stage_name
  auto_deploy = true
  default_route_settings {
    detailed_metrics_enabled = true
    throttling_burst_limit   = 100
    throttling_rate_limit    = 50
  }
}
