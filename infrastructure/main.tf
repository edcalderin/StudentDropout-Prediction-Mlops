terraform {
  required_version = ">=1.0"
  backend "s3" {
    bucket  = "tf-state-student-dropout"
    key     = "student-dropout.tfstate"
    region  = "us-east-2"
    encrypt = true
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
  repositories = {
    "backend" = {
      ecr_repo_name         = var.backend_repo_name
      image_tag_mutability  = "IMMUTABLE"
      scan_on_push          = true
    }

    "db" = {
      ecr_repo_name         = var.db_repo_name
      image_tag_mutability  = "IMMUTABLE"
      scan_on_push          = true
    }

    "streamlit" = {
      ecr_repo_name         = var.streamlit_repo_name
      image_tag_mutability  = "IMMUTABLE"
      scan_on_push          = true
    }

    "adminer" = {
      ecr_repo_name         = var.adminer_repo_name
      image_tag_mutability  = "IMMUTABLE"
      scan_on_push          = true
    }

    "grafana" = {
      ecr_repo_name = var.grafana_repo_name
      image_tag_mutability  = "IMMUTABLE"
      scan_on_push          = true
    }
  }
}

# Input events
module "source_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.project_id}-${var.source_stream_name}"
  shard_count      = 2
  retention_period = 48
  tags             = var.project_id
}

# Predictions
module "output_kinesis_stream" {
  source           = "./modules/kinesis"
  stream_name      = "${var.project_id}-${var.output_stream_name}"
  shard_count      = 2
  retention_period = 48
  tags             = var.project_id
}

# model bucket
module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = "${var.project_id}-${var.model_bucket}"
}

module "ecr_image" {
  source                     = "./modules/ecr"
  account_id                 = local.account_id

  lambda_function_local_path = var.lambda_function_local_path
  model_script_local_path    = var.model_script_local_path
  docker_image_local_path    = var.docker_image_local_path

  for_each = local.repositories

  ecr_repo_name              = "${var.project_id}-${each.ecr_repo_name}"
  image_tag_mutability       = each.value.image_tag_mutability
  scan_on_push               = each.value.scan_on_push
}

module "lambda_function" {
  source = "./modules/lambda"
  image_uri = module.ecr_image.image_url
  lambda_function_name = "${var.project_id}-${var.lambda_function_name}"
  model_bucket = module.s3_bucket.name
  output_stream_arn = module.output_kinesis_stream.stream_arn
  output_stream_name = "${var.project_id}-${var.output_stream_name}"
  source_stream_arn = module.source_kinesis_stream.stream_arn
  source_stream_name = "${var.project_id}-${var.source_stream_name}"
}

# CI/CD

output "lambda_function" {
  value = "${var.project_id}-${var.lambda_function_name}"
}

output "model_bucket" {
  value = "${var.project_id}-${var.model_bucket}"
}

output "ecr_repo" {
  value = "${var.project_id}-${var.ecr_repo_name}"
}

output "output_kinesis_stream" {
  value = "${var.project_id}-${var.output_stream_name}"
}
