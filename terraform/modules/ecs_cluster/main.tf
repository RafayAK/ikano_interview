###############################################################
# ECS Cluster Module
# Creates ECS cluster with Fargate & Fargate Spot capacity providers
###############################################################

module "cluster" {
  source  = "terraform-aws-modules/ecs/aws//modules/cluster"
  version = "5.12.1"

  cluster_name = var.cluster_name

  # Weighted distribution for cost-effectiveness:
  # FARGATE_SPOT (weight 2) cuts compute cost by up to 70%
  # FARGATE (weight 1) provides baseline fallback reliability
  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        weight = 1
      }
    }
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 2
      }
    }
  }

  create_cloudwatch_log_group            = true
  cloudwatch_log_group_name              = "/ecs/${var.cluster_name}"
  cloudwatch_log_group_retention_in_days = var.cloudwatch_log_group_retention_in_days

  tags = var.tags
}
