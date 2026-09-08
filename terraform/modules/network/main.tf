#######################################################################
# VPC Module
# Creates a VPC with public and private subnets, Internet Gateway, and
# optional NAT Gateway.
#######################################################################

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.21.0"

  name = var.name
  cidr = var.cidr

  azs             = var.azs
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway     = var.enable_nat_gateway
  single_nat_gateway     = var.enable_single_nat_gateway
  one_nat_gateway_per_az = false

  tags = var.tags
}
