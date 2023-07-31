# Students' dropout prediction

## Project Description
The objective of this project is to develop a robust machine learning model that accurately predicts student dropout in educational institutions using MLOps techniques. Leveraging AWS services like AWS Kinesis, ECR, S3, RDS, EC2, and Terraform for Infrastructure as Code (IaC), we will create an end-to-end data pipeline, complete with orchestration, streaming prediction, experiment tracking, and continuous integration/continuous deployment (CI/CD) using GitHub workflows. Additionally, the project will include unit and integration tests, along with built-in shell scripts for seamless automation and efficient model deployment.

### Problem Statement:
Student dropout is a critical concern in educational institutions, and early detection of at-risk students can significantly improve retention rates and student success. This project aims to build a predictive machine learning model that can effectively identify students at risk of dropping out, enabling timely intervention and support.

### Proposed Solution:
To address the challenge of student dropout, we will create a machine learning model using historical student data, including academic performance, socio-economic factors, and engagement metrics. This data will be processed, transformed, and fed into a predictive model that will forecast dropout probabilities for individual students.

### MLOps Techniques:
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

### Project Impact:

The successful implementation of this machine learning model using MLOps techniques on AWS and Terraform will equip educational institutions with a powerful tool to predict student dropout. By identifying at-risk students in advance, administrators and educators can intervene effectively, offering personalized support and resources to improve student retention and overall academic outcomes. Additionally, the integration of CI/CD workflows and automated shell scripts will enhance productivity, maintainability, and reproducibility of the entire pipeline, ensuring continuous improvement and scalability of the predictive model.






## MLFlow setup (EC2)

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

## Activate environment

```bash
source $(pipenv --venv)/Scripts/activate
python orchestration/train.py
python orchestration/deployment.py
```
 ```bash
 prefect agent start -p default-agent-pool
 ```
## Script for experiment tracking

```bash
python src/experiment_tracking.py
```
## Experiment tracking

### Prepare env

```bash
pipenv install
source $(pipenv --venv)/Scripts/activate
```

### Create experiment with different features

After doing EDA and obtaining features, it is required run `create_experiment.py` script to track this experiment.
Basically, it trains a pipeline with a XGBoost model using random hyperparameters.

```bash
python preprocess.py
```
Create first test experiment
```bash
python create_experiment.py
```

### Hyperparamenter-optimization step
Once selected the best model, run this command to optimize the model using the features on which it was trained originally.
Create a new MLFlow experiment with a set of models derived from Optuna optimizer.

```bash
python optuna.py
```

## References
* M.V.Martins, D. Tolledo, J. Machado, L. M.T. Baptista, V.Realinho. (2021) "Early prediction of student’s performance in higher education: a case study" Trends and Applications in Information Systems and Technologies, vol.1, in Advances in Intelligent Systems and Computing series. Springer. DOI: 10.1007/978-3-030-72657-7_16
