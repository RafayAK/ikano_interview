variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
  default     = "ikano-app-dev"
}

variable "image_tag_mutability" {
  description = "Tag mutability (MUTABLE or IMMUTABLE)"
  type        = string
  default     = "MUTABLE"
}

variable "force_delete" {
  description = "Delete repository even if containing images on teardown"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to assign"
  type        = map(string)
  default = {
    Project     = "Ikano-Onboarding"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}
