output "alb_dns_name" {
  description = "The public DNS name of the Application Load Balancer"
  value       = module.alb.dns_name
}

output "alb_url" {
  description = "The HTTP URL to access the deployed application"
  value       = "http://${module.alb.dns_name}"
}

output "ecr_repository_url" {
  description = "The URI of the pre-app ECR repository"
  value       = local.ecr_repository_url
}

output "docker_push_commands" {
  description = "Convenience commands to authenticate, build, tag, and push the image to ECR"
  value       = <<-EOT
    # 1. Authenticate Docker to AWS ECR
    aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${local.ecr_repository_url}

    # 2. Build the unified multi-stage container
    docker build -f prod.Dockerfile -t ${local.ecr_repository_url}:latest .

    # 3. Push to ECR
    docker push ${local.ecr_repository_url}:latest

    # 4. Trigger a fresh ECS deployment
    aws ecs update-service --cluster ${module.cluster.ecs_cluster_name} --service ${module.app_service.service_name} --force-new-deployment --region ${var.aws_region}
  EOT
}

output "rds_endpoint" {
  description = "The connection endpoint for the RDS PostgreSQL database (if managed RDS is enabled)"
  value       = var.use_managed_rds ? module.rds[0].endpoint : "External Database"
}

output "ecs_cluster_name" {
  description = "The name of the ECS cluster"
  value       = module.cluster.ecs_cluster_name
}

output "ecs_service_name" {
  description = "The name of the ECS service"
  value       = module.app_service.service_name
}
