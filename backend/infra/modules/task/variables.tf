variable "environment" {
    description = "Deployment environment (e.g. prod, green, dev, etc..)"
    type        = string
}

variable "bucket_prefix" {
    description = "Output bucket prefix"
    type        = string
    default     = "sportnumerics-rankings-bucket"
}

variable "subnets" {
    description = "Subnets for ECS task"
    type        = list(string)
    default     = ["subnet-53f5bb0a", "subnet-24bfda41"]
}

variable "image_tag" {
    description = "Docker image tag"
    type        = string
    default     = "latest"
}