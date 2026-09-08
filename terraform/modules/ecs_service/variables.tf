variable "name" {
  description = "The name of the ECS service."
  type        = string
}

variable "cluster_arn" {
  description = "The ARN of the ECS cluster."
  type        = string
}

variable "cpu" {
  description = "The number of CPU units to reserve for the task (e.g. 256 for 0.25 vCPU)."
  type        = number
  default     = 256
}

variable "memory" {
  description = "The amount of memory (in MiB) to reserve for the task (e.g. 512)."
  type        = number
  default     = 512
}

variable "container_definitions" {
  description = "A map of valid ECS container definitions."
  type        = any
}

variable "subnet_ids" {
  description = "A list of subnet IDs for the service."
  type        = list(string)
}

variable "assign_public_ip" {
  description = "Assign public IP to the ENI (required if running tasks in public subnets without NAT gateway)."
  type        = bool
  default     = false
}

variable "load_balancer" {
  description = "A map of load balancer configurations for the ECS service."
  type        = any
}

variable "network_mode" {
  description = "The Docker networking mode to use for containers."
  type        = string
  default     = "awsvpc"
}

variable "security_group_rules" {
  description = "A map of security group rules to apply to the ECS service."
  type        = any
  default     = {}
}

variable "launch_type" {
  description = "The launch type for the service (FARGATE)."
  type        = string
  default     = "FARGATE"
}

variable "tags" {
  description = "A map of tags to assign to the ECS service."
  type        = map(string)
  default     = {}
}

variable "autoscaling_min_capacity" {
  description = "Minimum number of tasks to run in the service."
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum number of tasks to run in the service."
  type        = number
  default     = 1
}

variable "desired_count" {
  description = "Number of instances of the task definition to place and keep running."
  type        = number
  default     = 1
}
