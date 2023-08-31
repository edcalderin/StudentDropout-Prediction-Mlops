# Load environment variables from .env file
include .env
export

LOCAL_TAG:=$(shell date +"%Y-%m-%d-%H-%M")
LOCAL_IMAGE_NAME:=stream-student-dropout-classifier:${LOCAL_TAG}

quality_checks:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint --recursive=y .

test:
	PYTHONPATH=. pipenv run pytest streaming/tests/

build: quality_checks test
	docker build -t ${LOCAL_IMAGE_NAME} .

integration_test: build
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} sh streaming/integration-tests/run.sh

publish: build integration_test
	LOCAL_IMAGE_NAME=${LOCAL_IMAGE_NAME} sh scripts/publish.sh

terraform_init_plan:
	cd infrastructure && terraform init && terraform plan -var-file=vars/var.tfvars

terraform_apply:
	cd infrastructure && terraform apply -var-file=vars/var.tfvars --auto-approve

setup:
	pipenv install pre-commit --dev
	pre-commmit install

deploy_manual:
	sh scripts/deploy-manual.sh

send_test_record:
	sh scripts/send-record.sh
