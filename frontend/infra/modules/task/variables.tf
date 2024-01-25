variable "environment" {
    description = "Deployment environment (e.g. prod, green, dev, etc..)"
    type        = string
}

variable "data_bucket_prefix" {
    description = "Data bucket prefix from backend"
    type        = string
    default     = "sportnumerics-rankings-bucket"
}

variable "website_domain" {
    description = "Domain for S3 bucket website"
    type        = string
    default = "s3.us-west-2.amazonaws.com"
}
