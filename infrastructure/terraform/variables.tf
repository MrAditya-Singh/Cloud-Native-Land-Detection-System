# Terraform variables

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}

variable "satellite_data_bucket_name" {
  description = "S3 bucket name for satellite data"
  type        = string
  default     = "land-detection-satellite-data"
}

variable "ml_models_bucket_name" {
  description = "S3 bucket name for ML models"
  type        = string
  default     = "land-detection-ml-models"
}

variable "results_bucket_name" {
  description = "S3 bucket name for results"
  type        = string
  default     = "land-detection-results"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "landdetection"
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "sagemaker_instance_type" {
  description = "SageMaker notebook instance type"
  type        = string
  default     = "ml.t3.medium"
}
