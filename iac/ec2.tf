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

# The EC2 instance for our web application
resource "aws_instance" "web_server" {
  ami           = data.aws_ami.amazon_linux_2.id
  instance_type = "t2.micro" # Free Tier eligible

  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.web_sg.id]

  # Requirement: Encryption at Rest for the server's storage
  root_block_device {
    encrypted = true
  }

  # This script runs when the instance first starts up
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y git python3-pip openssl 

              # Clone the application repository
              git clone https://github.com/Sheridan-College-FAST-CloudSecurity/gym-management-system.git /home/ec2-user/app

              # Install dependencies
              cd /home/ec2-user/app
              pip3 install -r requirements.txt
              pip3 install gunicorn

              # Generate a self-signed SSL certificate for HTTPS
              openssl req -x509 -newkey rsa:4096 -nodes \
                -keyout /home/ec2-user/app/key.pem \
                -out /home/ec2-user/app/cert.pem -days 365 \
                -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"

              # Create the .env file with secrets
              echo "FLASK_SECRET_KEY='${var.flask_secret_key}'" > /home/ec2-user/app/.env
              echo "DATABASE_URL='postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.gym_database.address}/${aws_db_instance.gym_database.db_name}'" >> /home/ec2-user/app/.env
              
              # Set permissions
              chown -R ec2-user:ec2-user /home/ec2-user/app

              # Run the application with Gunicorn over HTTPS on port 443
              gunicorn --bind 0.0.0.0:443 web_app:app --daemon --keyfile /home/ec2-user/app/key.pem --certfile /home/ec2-user/app/cert.pem
              EOF
  tags = {
    Name = "gym-web-server"
  }
}