###############################################################
# ECS Service Module
# Provisions Fargate service, task definition, and security groups
###############################################################

module "ecs_service" {
  source  = "terraform-aws-modules/ecs/aws//modules/service"
  version = "5.12.1"

  name        = var.name
  cluster_arn = var.cluster_arn

  cpu    = var.cpu
  memory = var.memory

  launch_type = var.launch_type

  container_definitions  = var.container_definitions
  enable_execute_command = true

  load_balancer = var.load_balancer

  assign_public_ip     = var.assign_public_ip
  subnet_ids           = var.subnet_ids
  security_group_rules = var.security_group_rules
  network_mode         = var.network_mode

  desired_count            = var.desired_count
  autoscaling_min_capacity = var.autoscaling_min_capacity
  autoscaling_max_capacity = var.autoscaling_max_capacity

  tags = var.tags
}
