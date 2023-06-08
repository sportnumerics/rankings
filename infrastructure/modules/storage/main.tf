
resource "aws_s3_bucket" "bucket" {
    bucket = "sportnumerics-rankings-bucket-${var.environment}"

    tags = {
        App = "rankings"
        Stage = var.environment
    }
}