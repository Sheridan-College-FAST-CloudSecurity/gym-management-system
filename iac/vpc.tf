# iac/vpc.tf

# The Virtual Private Cloud (VPC)
resource "aws_vpc" "gym_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "gym-vpc"
  }
}

# An Internet Gateway to allow public traffic
resource "aws_internet_gateway" "gym_igw" {
  vpc_id = aws_vpc.gym_vpc.id
  tags = {
    Name = "gym-igw"
  }
}

# Public Subnet for the Web Server (EC2)
resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.gym_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.region}a"
  map_public_ip_on_launch = true # Instances in this subnet get a public IP
  tags = {
    Name = "gym-public-subnet"
  }
}

# Private Subnet for the Database (RDS)
resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.gym_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.region}b"
  tags = {
    Name = "gym-private-subnet"
  }
}

# Route Table for the Public Subnet to route traffic to the Internet Gateway
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.gym_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gym_igw.id
  }

  tags = {
    Name = "gym-public-rt"
  }
}

# Associate the Public Route Table with the Public Subnet
resource "aws_route_table_association" "public_subnet_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}