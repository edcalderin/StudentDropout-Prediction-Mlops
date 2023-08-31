variable "lambda_function_name" {}

variable "source_stream_name" {
  type        = string
  description = "Source Kinesis Data Streams stream name"
}

variable "output_stream_name" {
    description = "Name of output stream where all the events will be passed"
}

variable "source_stream_arn" {}

variable "output_stream_arn" {}

variable "model_bucket" {}

variable "image_uri" {}
