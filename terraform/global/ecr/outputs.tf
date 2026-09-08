output "repository_url" {
  description = "The URI of the created ECR repository"
  value       = aws_ecr_repository.app.repository_url
}

output "repository_arn" {
  description = "The ARN of the ECR repository"
  value       = aws_ecr_repository.app.arn
}

output "repository_name" {
  description = "The name of the ECR repository"
  value       = aws_ecr_repository.app.name
}

output "docker_push_commands" {
  description = "Commands to build and push container to this repository"
  value       = <<-EOT
    # 1. Login to ECR
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.app.repository_url}

    # 2. Build production image
    docker build -f prod.Dockerfile -t ${aws_ecr_repository.app.repository_url}:latest .

    # 3. Push to ECR
    docker push ${aws_ecr_repository.app.repository_url}:latest
  EOT
}
