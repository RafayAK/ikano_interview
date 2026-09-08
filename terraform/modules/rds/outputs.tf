output "endpoint" {
  description = "The connection endpoint in address:port format"
  value       = aws_db_instance.postgres.endpoint
}

output "address" {
  description = "The hostname of the RDS instance"
  value       = aws_db_instance.postgres.address
}

output "port" {
  description = "The database port"
  value       = aws_db_instance.postgres.port
}

output "db_name" {
  description = "The database name"
  value       = aws_db_instance.postgres.db_name
}

output "db_username" {
  description = "The database username"
  value       = aws_db_instance.postgres.username
}

output "db_password" {
  description = "The database password"
  value       = local.db_password
  sensitive   = true
}

output "database_url" {
  description = "AsyncPG connection string formatted for FastAPI APP_DATABASE_URL"
  value       = "postgresql+asyncpg://${aws_db_instance.postgres.username}:${local.db_password}@${aws_db_instance.postgres.endpoint}/${aws_db_instance.postgres.db_name}"
  sensitive   = true
}
