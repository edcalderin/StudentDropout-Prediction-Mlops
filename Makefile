# Load environment variables from .env file
include .env
export

LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stream-student-dropout-classifier:${LOCAL_TAG}

quality_checks:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .

unit_tests:
	PYTHONPATH=. pipenv run pytest streaming/tests/

build: quality_checks unit_tests
	docker build -t ${LOCAL_IMAGE_NAME} .

integration_tests: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} sh streaming/integration-tests/run.sh

publish: build integration_tests
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} sh scripts/publish.sh

### Terraform local ###

terraform_init_plan:
	cd infrastructure && terraform init --reconfigure && terraform plan -var-file=vars/stg.tfvars

terraform_apply: terraform_init_plan
	cd infrastructure && terraform apply -var-file=vars/stg.tfvars --auto-approve

create_infrastructure: terraform_apply
	sh scripts/deploy-manual.sh

terraform_destroy:
	cd infrastructure && terraform destroy -var-file=vars/stg.tfvars --auto-approve

start_services:
	docker-compose up --build

######################

setup:
	pipenv install pre-commit --dev
	pre-commmit install
