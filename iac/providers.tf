terraform {
  backend "s3" {
    bucket = "gym-mgmt-tfstate-2023"  # Create this first manually
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.region
}