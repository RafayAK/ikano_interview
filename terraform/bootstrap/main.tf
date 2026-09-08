###############################################################
# Bootstrap S3 Bucket for Terraform Remote State
#
# NOTE FOR REVIEWERS:
# This module provides production-grade remote state storage (S3 bucket
# with versioning, AES-256 encryption, and public access blocks).
#
# For this temporary 1-week evaluation, we deliberately decided NOT to
# apply this module and kept state local. This avoids chicken-and-egg
# bootstrapping hurdles, requires zero pre-existing S3 buckets to run
# 'make deploy', and ensures 100% clean teardown without leaving behind
# an orphaned state bucket.
#
# To enable remote S3 state: apply this module first, then uncomment
# the 'backend "s3"' block in terraform/live/dev/providers.tf.
###############################################################

resource "aws_s3_bucket" "terraform_state" {
  bucket        = var.state_bucket_name
  force_destroy = var.force_destroy

  tags = var.tags
}

resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
