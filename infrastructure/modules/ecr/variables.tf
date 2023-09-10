variable "ecr_repo_name" {
  type        = string
  description = "ECR repo name"
}

variable "ecr_image_tag" {
  type        = string
  description = "ECR repo name"
  default     = "latest"
}

variable "lambda_function_local_path" {
  type        = string
  description = "Local path to lambda function / python file"
}

variable "model_script_local_path" {
  type        = string
  description = "Local path to model.py script"
}

variable "docker_image_local_path" {
  type        = string
  description = "Local path to Dockerfile"
}

variable "region" {
  type = string
  description = "region"
  default = "us-east-2"
}

variable "account_id" {
}

variable "image_tag_mutability" {
}

variable "scan_on_push" {}
