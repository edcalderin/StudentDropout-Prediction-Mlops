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

variable "backend_repo_name" {}
variable "streamlit_repo_name" {}
variable "db_repo_name" {}
variable "adminer_repo_name" {}
variable "grafana_repo_name" {}

variable "lambda_function_name" {}
