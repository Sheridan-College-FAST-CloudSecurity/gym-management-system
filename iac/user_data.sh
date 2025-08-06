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
echo "FLASK_SECRET_KEY='${flask_secret_key}'" > /home/ec2-user/app/.env
echo "DATABASE_URL='postgresql://${db_username}:${db_password}@${db_address}/${db_name}'" >> /home/ec2-user/app/.env

# Set permissions
chown -R ec2-user:ec2-user /home/ec2-user/app

# Run the application with Gunicorn over HTTPS on port 443
sleep 30
gunicorn --bind 0.0.0.0:443 web_app:app --daemon --keyfile /home/ec2-user/app/key.pem --certfile /home/ec2-user/app/cert.pem