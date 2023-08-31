resource "aws_lambda_function" "kinesis_lambda" {
  function_name = var.lambda_function_name
  package_type = "Image"
  image_uri = var.image_uri
  role = aws_iam_role.iam_lambda.arn
  memory_size = 512
  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {
      PREDICTIONS_OUTPUT_STREAM = var.output_stream_name
    }
  }

  timeout = 240
}

resource "aws_lambda_function_event_invoke_config" "kinesis_lambda_event" {
  function_name = aws_lambda_function.kinesis_lambda.function_name
  maximum_event_age_in_seconds = 60
  maximum_retry_attempts = 0
}

resource "aws_lambda_event_source_mapping" "kinesis_mapping" {
  event_source_arn = var.source_stream_arn
  function_name = aws_lambda_function.kinesis_lambda.function_name
  starting_position = "LATEST"
  depends_on = [
    aws_iam_role_policy_attachment.kinesis_processing
   ]
}
