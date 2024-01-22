variable "environment" {
    description = "Deployment environment (e.g. prod, green, dev, etc..)"
    type        = string
}

variable "data_bucket_prefix" {
    description = "Data bucket prefix from backend"
    type        = string
    default     = "sportnumerics-rankings-bucket"
}
