output "s3_bucket_name" {
  description = "Name of the created S3 state bucket"
  value       = aws_s3_bucket.terraform_state.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the created S3 state bucket"
  value       = aws_s3_bucket.terraform_state.arn
}
