variable "state_bucket_name" {
  description = "Globally unique name for the S3 state bucket"
  type        = string
  default     = "ikano-terraform-state-bucket"
}

variable "force_destroy" {
  description = "Allow bucket deletion even if non-empty (convenient for 1-week take-home teardown)"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to assign to the bucket"
  type        = map(string)
  default = {
    Project   = "Ikano"
    ManagedBy = "Terraform"
  }
}
