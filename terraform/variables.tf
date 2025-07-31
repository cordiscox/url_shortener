variable "aws_region" {
  description = "The AWS region where resources will be deployed."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "A name for the project, used as a prefix for resources."
  type        = string
  default     = "url-shortener"
}

variable "image_uri" {
  description = "The full URI of the Docker image in Amazon ECR."
  type        = string
}

variable "container_port" {
  description = "The port that the container exposes."
  type        = number
  default     = 8000
}