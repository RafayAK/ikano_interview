###############################################################
# RDS PostgreSQL Module
# Provisions a cost-effective, single-AZ PostgreSQL 16 instance
# for the take-home evaluation with clean 1-week teardown.
###############################################################

resource "random_password" "master_password" {
  length  = 16
  special = false # Avoid special characters that can complicate URL escaping
}

locals {
  db_password = var.db_password != null && var.db_password != "" ? var.db_password : random_password.master_password.result
}

resource "aws_db_subnet_group" "rds" {
  name        = "${var.name}-subnet-group"
  subnet_ids  = var.subnet_ids
  description = "Database subnet group for ${var.name}"

  tags = var.tags
}

resource "aws_security_group" "rds" {
  name        = "${var.name}-rds-sg"
  description = "Security group for ${var.name} PostgreSQL RDS"
  vpc_id      = var.vpc_id

  # Allow ingress exclusively from the ECS service security group
  ingress {
    description     = "PostgreSQL from ECS service"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ecs_security_group_id]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_db_instance" "postgres" {
  identifier = var.name

  engine         = "postgres"
  engine_version = var.engine_version
  instance_class = var.instance_class

  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = local.db_password
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  multi_az            = false # Single-AZ for take-home evaluation cost savings

  # Deliberate teardown settings: Allows smooth 'terraform destroy' without blocking
  skip_final_snapshot = true
  deletion_protection = false

  tags = var.tags
}
