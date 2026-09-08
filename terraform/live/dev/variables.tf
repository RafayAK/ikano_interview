#############################################################################
# General Environment Variables
#############################################################################

variable "env" {
  description = "Environment name (e.g. dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

#############################################################################
# Networking (VPC)
#############################################################################

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "vpc_availability_zones" {
  description = "Availability Zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "vpc_public_subnets" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "vpc_private_subnets" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway in VPC. Set true for private subnet internet access. If false, tasks can be deployed to public subnets to save ~$32/mo."
  type        = bool
  default     = true
}

#############################################################################
# Application Container & ECS
#############################################################################

variable "app_cpu" {
  description = "Fargate task CPU allocation (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "app_memory" {
  description = "Fargate task Memory allocation in MiB (512 MiB)"
  type        = number
  default     = 512
}

variable "app_min_capacity" {
  description = "Minimum number of ECS tasks to run"
  type        = number
  default     = 1
}

variable "app_max_capacity" {
  description = "Maximum number of ECS tasks to run (pinned to 1 for cost-effective evaluation)"
  type        = number
  default     = 1
}

variable "container_name" {
  description = "Name of the application container"
  type        = string
  default     = "ikano-app"
}

variable "ecr_repository_name" {
  description = "Name of the pre-created ECR repository"
  type        = string
  default     = "ikano-app-dev"
}

variable "container_image" {
  description = "Docker image URI to run. Leave empty to default to latest in the created ECR repo."
  type        = string
  default     = ""
}

variable "log_retention_in_days" {
  description = "Days to retain CloudWatch logs"
  type        = number
  default     = 7
}

#############################################################################
# Database (RDS PostgreSQL)
#############################################################################

variable "use_managed_rds" {
  description = "Whether to provision an AWS RDS PostgreSQL instance. If false, set external_database_url."
  type        = bool
  default     = true
}

variable "external_database_url" {
  description = "Existing PostgreSQL asyncpg connection URL (e.g. Neon, Supabase) if use_managed_rds is false."
  type        = string
  default     = ""
  sensitive   = true
}

variable "db_engine_version" {
  description = "RDS PostgreSQL engine version (e.g. 18.3, 16.15)"
  type        = string
  default     = "18.3"
}

variable "db_instance_class" {
  description = "RDS instance class (db.t4g.micro is AWS free tier eligible)"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_name" {
  description = "Postgres database name"
  type        = string
  default     = "ikano_onboarding"
}

variable "db_username" {
  description = "Postgres master username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Postgres master password (leave blank to auto-generate)"
  type        = string
  default     = ""
  sensitive   = true
}

#############################################################################
# Optional HTTPS (ACM)
#############################################################################

variable "certificate_arn" {
  description = "Optional ACM certificate ARN to enable HTTPS listener on port 443"
  type        = string
  default     = ""
}
