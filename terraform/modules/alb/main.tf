locals {
  http_port    = 80
  https_port   = 443
  any_protocol = "-1"
  tcp_protocol = "tcp"
}

module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "9.16.0"

  name = var.name

  vpc_id  = var.vpc_id
  subnets = var.subnets

  load_balancer_type         = "application"
  enable_deletion_protection = var.enable_deletion_protection

  # Ingress rules: allow HTTP (80) and HTTPS (443)
  security_group_ingress_rules = {
    http_ingress = {
      description = "Allow HTTP from the internet"
      from_port   = local.http_port
      to_port     = local.http_port
      ip_protocol = local.tcp_protocol
      cidr_ipv4   = var.allowed_ingress_cidr
    }
    https_ingress = {
      description = "Allow HTTPS from the internet"
      from_port   = local.https_port
      to_port     = local.https_port
      ip_protocol = local.tcp_protocol
      cidr_ipv4   = var.allowed_ingress_cidr
    }
  }

  # Egress rules: restrict to VPC CIDR for backend/internal services
  security_group_egress_rules = {
    all_out_vpc = {
      description = "Egress to VPC"
      ip_protocol = local.any_protocol
      cidr_ipv4   = var.vpc_cidr_block
    }
    out_internet = {
      description = "Outbound internet access"
      from_port   = local.https_port
      to_port     = local.https_port
      ip_protocol = local.tcp_protocol
      cidr_ipv4   = "0.0.0.0/0"
    }
  }

  target_groups = var.target_groups

  tags = var.tags
}
