terraform {
  required_version = ">= 1.5.0"

  # Backend state configuration:
  # For local evaluation, state is stored locally by default.
  # To use S3 remote state (after running terraform/bootstrap), uncomment the block below:
  # backend "s3" {
  #   bucket  = "ikano-terraform-state-bucket"
  #   key     = "live/dev/terraform.tfstate"
  #   region  = "us-east-1"
  #   encrypt = true
  # }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "Ikano-Onboarding"
      Environment = var.env
      ManagedBy   = "Terraform"
      Repository  = "python-studies/Ikano"
    }
  }
}
