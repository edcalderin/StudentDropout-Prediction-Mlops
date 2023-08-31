resource "aws_ecr_repository" "repo" {
  name = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource null_resource ecr_image {
  triggers = {
    python_file = md5(file(var.lambda_function_local_path))
    docker_file = md5(file(var.docker_image_local_path))
    model_file  = md5(file(var.model_script_local_path))
  }

  provisioner "local-exec" {
    command = <<EOF
      aws ecr get-login-password --region ${var.region} | docker login --username AWS --password-stdin ${var.account_id}.dkr.ecr.${var.region}.amazonaws.com
      cd ../
      docker build -t ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag} .
      docker push ${aws_ecr_repository.repo.repository_url}:${var.ecr_image_tag}
    EOF
    interpreter = ["bash", "-c"] # For Linux/MacOS
  }
}

data aws_ecr_image lambda_image {
  depends_on = [ null_resource.ecr_image ]
  repository_name = var.ecr_repo_name
  image_tag = var.ecr_image_tag
}

output "image_url" {
  description = "ECR Url"
  value = "${aws_ecr_repository.repo.repository_url}:${data.aws_ecr_image.lambda_image.image_tag}"
}
