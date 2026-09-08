output "dns_name" {
  description = "Public DNS name of the ALB"
  value       = module.alb.dns_name
}

output "load_balancer_arn" {
  description = "The ARN of the Load Balancer"
  value       = module.alb.arn
}

output "security_group_id" {
  description = "Security group ID of the ALB"
  value       = module.alb.security_group_id
}

output "target_groups" {
  description = "Map of target group objects keyed by target group names"
  value       = module.alb.target_groups
}
