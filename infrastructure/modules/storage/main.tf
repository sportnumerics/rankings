
resource "aws_s3_bucket" "bucket" {
    bucket = "sportnumerics-rankings-bucket-${var.environment}"

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}

resource "aws_s3_bucket_public_access_block" "bucket" {
    bucket = aws_s3_bucket.bucket.id
}

resource "aws_s3_bucket_website_configuration" "website" {
    bucket = aws_s3_bucket.bucket.id

    index_document {
      suffix = "index.html"
    }

    error_document {
      key = "error.html"
    }
}