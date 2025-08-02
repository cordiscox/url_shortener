variable "aws_region" {
  description = "The AWS region where resources will be created."
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Project name, used as a prefix for resources."
  type        = string
  default     = "url-shortener"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for the public subnets."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "container_image" {
  description = "The full URI of the Docker image in ECR."
  type        = string
}

variable "container_port" {
  description = "The port on which the application listens inside the container."
  type        = number
  default     = 8000
}

variable "cpu" {
  description = "CPU units to assign to the Fargate task."
  type        = number
  default     = 256
}

variable "memory" {
  description = "Memory in MiB to assign to the Fargate task."
  type        = number
  default     = 512
}