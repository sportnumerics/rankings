terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  backend "s3" {
    bucket = "sportnumerics-rankings-terraform-state"
    key    = "infrastructure/prod.tfstate"
    region = "us-west-2"
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region = "us-west-2"
}

module "storage" {
  source = "../../modules/storage"

  environment = "prod"
}

module "cicd" {
  source = "../../modules/cicd"
}
