variable "name" {
  description = "Name of the ALB"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where the ALB will be created"
  type        = string
}

variable "subnets" {
  description = "List of public subnet IDs where the ALB will be created"
  type        = list(string)
}

variable "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  type        = string
}

variable "target_groups" {
  description = "Map of target group definitions"
  type        = any
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for the ALB (set to false for temporary environments)"
  type        = bool
  default     = false
}

variable "allowed_ingress_cidr" {
  description = "Allowed CIDR block to allow ingress traffic from"
  type        = string
  default     = "0.0.0.0/0"
}

variable "tags" {
  description = "Tags to assign to the ALB"
  type        = map(string)
  default     = {}
}
