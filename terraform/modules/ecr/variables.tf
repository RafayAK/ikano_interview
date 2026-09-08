variable "repository_name" {
  description = "Name of the ECR repository"
  type        = string
}

variable "image_tag_mutability" {
  description = "Tag mutability setting for image repository (MUTABLE or IMMUTABLE)"
  type        = string
  default     = "MUTABLE"
}

variable "force_delete" {
  description = "If true, will delete the repository even if it contains images (ideal for temporary/dev)"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to assign to the ECR repository"
  type        = map(string)
  default     = {}
}
