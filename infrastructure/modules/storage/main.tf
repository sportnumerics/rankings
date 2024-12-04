
resource "aws_s3_bucket" "bucket" {
  bucket = "sportnumerics-rankings-bucket-${var.environment}"

  tags = {
    App   = "rankings"
    Stage = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "bucket" {
  bucket = aws_s3_bucket.bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
