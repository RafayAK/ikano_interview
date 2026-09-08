variable "name" {
  description = "Identifier for the RDS instance and related resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the RDS instance is placed"
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet IDs for the RDS subnet group"
  type        = list(string)
}

variable "ecs_security_group_id" {
  description = "Security group ID of the ECS service allowed to connect to RDS"
  type        = string
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "18.3"
}

variable "instance_class" {
  description = "RDS instance class (db.t4g.micro is AWS free tier eligible)"
  type        = string
  default     = "db.t4g.micro"
}

variable "allocated_storage" {
  description = "Initial allocated storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Max storage allocation for autoscaling in GB (set equal to allocated_storage to disable autoscaling)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "Name of the default database to create"
  type        = string
  default     = "ikano_onboarding"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master database password (leave null/empty to auto-generate a secure random password)"
  type        = string
  default     = null
  sensitive   = true
}

variable "tags" {
  description = "Tags to assign to RDS resources"
  type        = map(string)
  default     = {}
}
