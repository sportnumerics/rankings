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
    default     = ["subnet-f728fa92", "subnet-866f9ff1", "subnet-cb183ce3", "subnet-c09b8b86"]
}

variable "image_tag" {
    description = "Docker image tag"
    type        = string
    default     = "latest"
}