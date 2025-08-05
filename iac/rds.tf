# iac/rds.tf

# This creates a subnet group, telling RDS which private subnets it can use
resource "aws_db_subnet_group" "gym_db_subnet_group" {
  name       = "gym-db-subnet-group"
  subnet_ids = [aws_subnet.private_subnet.id]

  tags = {
    Name = "Gym DB Subnet Group"
  }
}

# This is the RDS PostgreSQL database instance
resource "aws_db_instance" "gym_database" {
  identifier                     = "gym-mgmt-db"
  instance_class                 = "db.t3.micro"       # Free Tier eligible
  allocated_storage              = 20                  # In GiB
  engine                         = "postgres"
  engine_version                 = "15"
  db_name                        = "gym_db"
  username                       = var.db_username
  password                       = var.db_password
  db_subnet_group_name           = aws_db_subnet_group.gym_db_subnet_group.name
  vpc_security_group_ids         = [aws_security_group.db_sg.id]
  skip_final_snapshot            = true

  # Requirement: Encryption at Rest
  storage_encrypted              = true

  # FIXES: Enable auto minor version upgrades, deletion protection, and performance insights
  auto_minor_version_upgrade     = true
  deletion_protection            = true  # <-- CORRECTED ARGUMENT NAME
  performance_insights_enabled   = true
  copy_tags_to_snapshot          = true
}