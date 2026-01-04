# Terraform configuration for Cloud-Native Land Detection System

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 Buckets for data storage
resource "aws_s3_bucket" "satellite_data" {
  bucket = var.satellite_data_bucket_name
  
  tags = {
    Name        = "Satellite Data Bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "ml_models" {
  bucket = var.ml_models_bucket_name
  
  tags = {
    Name        = "ML Models Bucket"
    Environment = var.environment
  }
}

resource "aws_s3_bucket" "results" {
  bucket = var.results_bucket_name
  
  tags = {
    Name        = "Results Bucket"
    Environment = var.environment
  }
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "satellite_data" {
  bucket = aws_s3_bucket.satellite_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "ml_models" {
  bucket = aws_s3_bucket.ml_models.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# RDS PostgreSQL Database
resource "aws_db_instance" "main" {
  identifier           = "land-detection-db"
  engine              = "postgres"
  engine_version      = "15.4"
  instance_class      = var.db_instance_class
  allocated_storage   = 100
  storage_type        = "gp3"
  
  db_name  = "land_detection"
  username = var.db_username
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  skip_final_snapshot    = var.environment != "production"
  
  tags = {
    Name        = "Land Detection Database"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "land-detection-cache"
  engine              = "redis"
  node_type           = var.redis_node_type
  num_cache_nodes     = 1
  parameter_group_name = "default.redis7"
  engine_version      = "7.0"
  port                = 6379
  
  security_group_ids = [aws_security_group.redis.id]
  subnet_group_name  = aws_elasticache_subnet_group.main.name
  
  tags = {
    Name        = "Land Detection Cache"
    Environment = var.environment
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "land-detection-cluster"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name        = "Land Detection ECS Cluster"
    Environment = var.environment
  }
}

# SageMaker Notebook Instance for ML development
resource "aws_sagemaker_notebook_instance" "ml_dev" {
  name          = "land-detection-ml-dev"
  role_arn      = aws_iam_role.sagemaker.arn
  instance_type = var.sagemaker_instance_type
  
  tags = {
    Name        = "Land Detection ML Development"
    Environment = var.environment
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/land-detection"
  retention_in_days = 30
  
  tags = {
    Name        = "Land Detection Logs"
    Environment = var.environment
  }
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name        = "Land Detection VPC"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  
  tags = {
    Name = "Private Subnet 1"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  
  tags = {
    Name = "Private Subnet 2"
  }
}

resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.101.0/24"
  availability_zone = "${var.aws_region}a"
  
  tags = {
    Name = "Public Subnet 1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.102.0/24"
  availability_zone = "${var.aws_region}b"
  
  tags = {
    Name = "Public Subnet 2"
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "land-detection-db-subnet"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
  
  tags = {
    Name = "Land Detection DB Subnet Group"
  }
}

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "main" {
  name       = "land-detection-cache-subnet"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

# Security Groups
resource "aws_security_group" "db" {
  name        = "land-detection-db-sg"
  description = "Security group for RDS database"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "redis" {
  name        = "land-detection-redis-sg"
  description = "Security group for Redis cache"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# IAM Role for SageMaker
resource "aws_iam_role" "sagemaker" {
  name = "land-detection-sagemaker-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "sagemaker.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker" {
  role       = aws_iam_role.sagemaker.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

# Outputs
output "satellite_data_bucket" {
  value = aws_s3_bucket.satellite_data.bucket
}

output "ml_models_bucket" {
  value = aws_s3_bucket.ml_models.bucket
}

output "results_bucket" {
  value = aws_s3_bucket.results.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}
