# iac/iam.tf

resource "aws_iam_role" "web_server_role" {
  name = "gym-web-server-role"

  # This policy allows the EC2 service to assume this role
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "web_server_profile" {
  name = "gym-web-server-profile"
  role = aws_iam_role.web_server_role.name
}