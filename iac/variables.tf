# iac/variables.tf

variable "region" {
  description = "The AWS region to deploy resources in."
  default     = "us-east-1"
}

variable "db_username" {
  description = "The username for the RDS database."
  default     = "admin"
}

variable "db_password" {
  description = "The password for the RDS database."
  type        = string
  sensitive   = true # This tells Terraform not to show the password in logs
}

# iac/variables.tf

variable "flask_secret_key" {
  description = "The secret key for the Flask application."
  type        = string
  sensitive   = true
}

