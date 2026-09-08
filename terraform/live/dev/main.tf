###########################################################################
# Local variables
###########################################################################

locals {
  http_port    = 80
  https_port   = 443
  app_port     = 8000
  tcp_protocol = "tcp"
  any_protocol = "-1"
  any_port     = 0
  all_ips      = ["0.0.0.0/0"]

  # Pre-App ECR Repository URL (constructed from AWS account and region to avoid extra IAM permissions)
  ecr_repository_url = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.ecr_repository_name}"

  # Default to latest image in ECR if no external image specified
  container_image = var.container_image != "" ? var.container_image : "${local.ecr_repository_url}:latest"

  # Connection string: Managed RDS or external URL
  database_url = var.use_managed_rds ? module.rds[0].database_url : var.external_database_url

  # Subnets & public IP assignment:
  # When NAT Gateway is enabled, tasks live safely in private subnets with egress via NAT.
  # When NAT Gateway is disabled (to save ~$32/mo for quick tests), tasks run in public subnets with public IP.
  ecs_subnets          = var.enable_nat_gateway ? module.vpc.private_subnet_ids : module.vpc.public_subnet_ids
  ecs_assign_public_ip = !var.enable_nat_gateway
}

###########################################################################
# Caller Identity & Region
###########################################################################

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

###########################################################################
# VPC and Networking
###########################################################################

module "vpc" {
  source = "../../modules/network"

  name                      = "ikano-${var.env}-vpc"
  cidr                      = var.vpc_cidr
  azs                       = var.vpc_availability_zones
  private_subnets           = var.vpc_private_subnets
  public_subnets            = var.vpc_public_subnets
  enable_nat_gateway        = var.enable_nat_gateway
  enable_single_nat_gateway = true

  tags = {
    Environment = var.env
  }
}

###########################################################################
# Application Load Balancer (ALB)
###########################################################################

module "alb" {
  source = "../../modules/alb"

  name                       = "ikano-${var.env}-alb"
  vpc_id                     = module.vpc.vpc_id
  subnets                    = module.vpc.public_subnet_ids
  vpc_cidr_block             = module.vpc.vpc_cidr_block
  enable_deletion_protection = false # Clean teardown for take-home evaluation

  target_groups = {
    app = {
      name_prefix = "ikano-"
      port        = local.app_port
      target_type = "ip"
      protocol    = "HTTP"

      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 15
        matcher             = 200
        path                = "/health"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 3
      }

      create_attachment = false
    }
  }

  tags = {
    Environment = var.env
  }
}

# HTTP Listener: Reviews/evaluators can immediately open the ALB URL without SSL/DNS setup
resource "aws_lb_listener" "http" {
  load_balancer_arn = module.alb.load_balancer_arn
  port              = local.http_port
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = module.alb.target_groups["app"].arn
  }
}

# Optional HTTPS Listener: Activated if certificate_arn is provided
resource "aws_lb_listener" "https" {
  count             = var.certificate_arn != "" ? 1 : 0
  load_balancer_arn = module.alb.load_balancer_arn
  port              = local.https_port
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = module.alb.target_groups["app"].arn
  }
}

###########################################################################
# ECS Cluster (Fargate & Fargate Spot)
###########################################################################

module "cluster" {
  source = "../../modules/ecs_cluster"

  cluster_name                           = "ikano-${var.env}-cluster"
  cloudwatch_log_group_retention_in_days = var.log_retention_in_days

  tags = {
    Environment = var.env
  }
}

###########################################################################
# RDS PostgreSQL Instance
###########################################################################

module "rds" {
  count  = var.use_managed_rds ? 1 : 0
  source = "../../modules/rds"

  name                  = "ikano-${var.env}-pg"
  vpc_id                = module.vpc.vpc_id
  subnet_ids            = module.vpc.private_subnet_ids
  ecs_security_group_id = module.app_service.security_group_id

  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  db_name        = var.db_name
  db_username    = var.db_username
  db_password    = var.db_password != "" ? var.db_password : null

  tags = {
    Environment = var.env
  }
}

###########################################################################
# ECS Service (Unified FastAPI + Astro Container)
###########################################################################

module "app_service" {
  source = "../../modules/ecs_service"

  name        = "ikano-${var.env}-service"
  cluster_arn = module.cluster.ecs_cluster_arn
  cpu         = var.app_cpu
  memory      = var.app_memory

  autoscaling_min_capacity = var.app_min_capacity
  autoscaling_max_capacity = var.app_max_capacity

  container_definitions = {
    (var.container_name) = {
      cpu       = var.app_cpu
      memory    = var.app_memory
      essential = true
      image     = local.container_image

      readonly_root_filesystem = false

      port_mappings = [
        {
          name          = var.container_name
          containerPort = local.app_port
          hostPort      = local.app_port
          protocol      = local.tcp_protocol
        }
      ]

      environment = [
        {
          name  = "APP_DATABASE_URL"
          value = local.database_url
        },
        {
          name  = "APP_LOG_LEVEL"
          value = "INFO"
        },
        {
          name  = "APP_COOKIE_SECURE"
          value = var.certificate_arn != "" ? "true" : "false"
        },
        {
          name  = "APP_CORS_ALLOW_ORIGINS"
          value = "[\"*\"]"
        }
      ]
    }
  }

  load_balancer = {
    service = {
      target_group_arn = module.alb.target_groups["app"].arn
      container_name   = var.container_name
      container_port   = local.app_port
    }
  }

  assign_public_ip = local.ecs_assign_public_ip
  subnet_ids       = local.ecs_subnets

  security_group_rules = {
    egress_all = {
      type        = "egress"
      from_port   = local.any_port
      to_port     = local.any_port
      protocol    = local.any_protocol
      cidr_blocks = local.all_ips
    }

    ingress_alb = {
      type                     = "ingress"
      from_port                = local.app_port
      to_port                  = local.app_port
      description              = "Allow traffic from ALB to unified app service"
      protocol                 = local.tcp_protocol
      source_security_group_id = module.alb.security_group_id
    }
  }

  tags = {
    Environment = var.env
  }
}

