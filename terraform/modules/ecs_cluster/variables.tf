variable "cluster_name" {
  description = "The name of the ECS cluster."
  type        = string
}

variable "cloudwatch_log_group_retention_in_days" {
  description = "The number of days to retain log events in CloudWatch."
  type        = number
  default     = 7
}

variable "tags" {
  description = "A map of tags to assign to the ECS cluster."
  type        = map(string)
  default     = {}
}
