# iac/ec2.tf

# This looks up the latest Amazon Linux 2 AMI ID for us
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# This reads our user_data.sh script and injects variables into it
data "template_file" "user_data_script" {
  template = file("${path.module}/user_data.sh")

  vars = {
    db_username      = var.db_username
    db_password      = var.db_password
    db_address       = aws_db_instance.gym_database.address
    db_name          = aws_db_instance.gym_database.db_name
    flask_secret_key = var.flask_secret_key
  }
}

# The EC2 instance for our web application
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro" # Free Tier eligible

  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.web_server_profile.name # FIX: Attaches IAM role

  # FIX: Enable detailed monitoring
  monitoring = true

  # FIX: Enforce Instance Metadata Service v2 (more secure)
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Requirement: Encryption at Rest for the server's storage
  root_block_device {
    encrypted = true
  }

  # This passes the rendered script to the instance
  user_data = data.template_file.user_data_script.rendered
  
  # This ensures that if the user_data script changes, the instance is replaced
  user_data_replace_on_change = true

  tags = {
    Name = "gym-web-server"
  }
}