# Students' dropout prediction

## Project Description
The objective of this project is to develop a robust machine learning model that accurately predicts student dropout in educational institutions using MLOps techniques. Leveraging AWS services like AWS Kinesis, ECR, S3, RDS, EC2, and Terraform for Infrastructure as Code (IaC), we will create an end-to-end data pipeline, complete with orchestration, streaming prediction, experiment tracking, and continuous integration/continuous deployment (CI/CD) using GitHub workflows. Additionally, the project will include unit and integration tests, along with built-in shell scripts for seamless automation and efficient model deployment.

### Problem Statement:
Student dropout is a critical concern in educational institutions, and early detection of at-risk students can significantly improve retention rates and student success. This project aims to build a predictive machine learning model that can effectively identify students at risk of dropping out, enabling timely intervention and support.

### Proposed Solution:
To address the challenge of student dropout, we will create a machine learning model using historical student data, including academic performance, socio-economic factors, and engagement metrics. This data will be processed, transformed, and fed into a predictive model that will forecast dropout probabilities for individual students.

### Project Impact:

The successful implementation of this machine learning model using MLOps techniques on AWS and Terraform will equip educational institutions with a powerful tool to predict student dropout. By identifying at-risk students in advance, administrators and educators can intervene effectively, offering personalized support and resources to improve student retention and overall academic outcomes. Additionally, the integration of CI/CD workflows and automated shell scripts will enhance productivity, maintainability, and reproducibility of the entire pipeline, ensuring continuous improvement and scalability of the predictive model.

## MLOps tools

1. Data Collection and Storage:

* Raw data will be collected from UCI (UC Irvine Machine Learning Repository).

2. Data Preprocessing and Feature Engineering:

* Preprocessing steps, such as encoding categorical variables and feature creation, will be applied to prepare the data for model training.

3. Model Development and Experiment Tracking:

* We will experiment with multiple machine learning algorithms to identify the best-performing model for dropout prediction.

4. Model Orchestration and Deployment:

* AWS Step Functions will be employed for creating serverless workflows to orchestrate the entire model training, evaluation, and deployment process.
* Terraform will be used for Infrastructure as Code (IaC) to define the AWS resources required for model deployment, ensuring consistency and reproducibility.

5. Streaming Prediction:

* AWS Kinesis Data Streams will enable real-time prediction on incoming data, allowing for proactive identification of students at immediate risk of dropping out.

6. Continuous Integration/Continuous Deployment (CI/CD):

* GitHub workflows will be set up for continuous integration and continuous deployment, automating the process of testing, building, and deploying model updates.

7. Unit and Integrations Tests:

* Unit tests will be created to verify the functionality of individual components of the model and data pipeline.
* Integration tests will validate the interactions between different components, ensuring smooth data flow.

8. Shell Scripts for Automation:

* Shell scripts will be built-in to automate various tasks, such as data preprocessing, model training, and deployment.

## Directory layout
```
.
├── .github                          # CI/CD workflows
├── images/                          # Assets
├── model_monitoring/                # CI/CD workflowsDirectory for monitoring the model
├── notebooks/                       # Notebooks used to analysis prior to development
├── orchestration/                   # Directory for workflow orchestration-related files
├── streaming/                       # Directory for handling streaming dataastAPI directoryF
|   ├── integration-tests/           # Integration tests for the streaming module
|   |   ├── artifacts/               # Files to manage global configuration variables and settings
|   |   |   ├── encoders/            # Pickle files of LabelEncoder
|   |   |   ├── model/               # Files related to the model
|   ├── tests/                       # Unit tests for the streaming module
|   ├── lambda_function.py           # Entrypoint for the application
|   ├── model.py                     # Functions and classes related to the model
├── .pre-commit-config.yaml          # Configuration file for pre-commit hooks
├── Dockerfile                       # Docker configuration for building the application
├── Makefile                         # Configuration of commands to automate the applications
├── Pipfile                          # Requirements for development and production
├── Pipfile.lock                     # Lock file for Pipfile dependencies
└── pyproject.toml                   # Project metadata and dependencies (PEP 518)
└── README.md
```

## Notebooks

Run notebooks to conduct Exploratory Data Analysis and experiment with features selection and feature creation using Feature-engine module ideally created for these purposes. Diverse experiments were carry out using RandomForest, SVM, XGBoost, with the latter showing the best performance. The resultant features were persistent into a yaml file containing other global properties. In this project, just 7 features were extracted out of the 37 original through Recursive Feature Addition technique.


## MLFlow and Orchestration

### Setup in EC2

```bash
sudo yum update
yum install pip
pip install mlflow psycopg2-binary
mlflow server \
        --host 0.0.0.0 \
        --port 5000 \
        --default-artifact-root ${BUCKET} \
        --backend-store-uri postgresql://${USER}:${PASSWORD}@${HOST}:5432/${DB_NAME}
```

### Activate environment

```bash
source $(pipenv --venv)/Scripts/activate
```

Prepare the following variables:
```bash
export MLFLOW_TRACKING_URI=ec2-xxxxxx.region.compute.amazonaws.com
export PYTHONPATH=.
```
* Training workflow: Get data, preprocess, train and register model

```bash
python orchestration/train.py
```

![Alt text](./images/prefect-run.PNG)

* Or execute them separately if you wish to experiment with other models or hyperparams:

```bash
python orchestration/preprocess.py
python orchestration/create_experiment.py (Optional) Used to test with different models
python orchestration/optimize.py
```

* Finally, deployment:

 ```bash
python orchestration/deployment.py
prefect agent start -p default-agent-pool
 ```

## Streaming deployment

```bash
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxxo
export AWS_DEFAULT_REGION=us-east-2
export ECR_IMAGE=###

aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin ${ECR_IMAGE}
docker build -t stream-student-dropout-classifier .
docker tag stream-student-dropout-classifier:latest ${ECR_IMAGE}/stream-student-dropout-classifier:latest
docker push ${ECR_IMAGE}/stream-student-dropout-classifier:latest
```

Sending data

```bash
KINESIS_STREAM_INPUT=student-dropout-input-stream

aws kinesis put-record \
        --stream-name $KINESIS_STREAM_INPUT \
        --partition-key 1 \
        --data '{
                "student_features" : {
                        "GDP": 1.74,
                        "Inflation rate": 1.4,
                        "Tuition fees up to date": 1,
                        "Scholarship holder": 0,
                        "Curricular units 1st sem (approved)": 5,
                        "Curricular units 1st sem (enrolled)": 6,
                        "Curricular units 2nd sem (approved)": 5
                },
                "student_id": 256
                }' \
        --cli-binary-format raw-in-base64-out
```

Reading from the stream

```bash
KINESIS_STREAM_OUTPUT=student-dropout-output-stream
SHARD=shardId-000000000000

SHARD_ITERATOR=$(aws kinesis get-shard-iterator \
        --shard-id ${SHARD} \
        --shard-iterator-type TRIM_HORIZON \
        --stream-name ${KINESIS_STREAM_OUTPUT} \
        --query 'ShardIterator'
)

RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)

echo ${RESULT}
```

## Run tests

Run

```bash
make integration_test
```

## References
* M.V.Martins, D. Tolledo, J. Machado, L. M.T. Baptista, V.Realinho. (2021) "Early prediction of student’s performance in higher education: a case study" Trends and Applications in Information Systems and Technologies, vol.1, in Advances in Intelligent Systems and Computing series. Springer. DOI: 10.1007/978-3-030-72657-7_16

* Feature-engine: https://feature-engine.trainindata.com/en/latest/
