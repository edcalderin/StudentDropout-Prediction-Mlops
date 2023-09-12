variable "region" {
  default = "us-east-2"
}

variable "project_id" {
  description = "project_id"
  default     = "student-dropout"
}

# KINESIS
variable "source_stream_name" {}
variable "output_stream_name" {}

# S3
variable "model_bucket" {}

# ECR
variable "lambda_function_local_path" {
  description = ""
}

variable "model_script_local_path" {
  description = ""
}

variable "docker_image_local_path" {
  description = ""
}

variable "lambda_function_name" {}

variable "ecr_repo_name" {
  description = ""
}
