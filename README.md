# Students' dropout prediction

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
```

## Script for experiment tracking

```bash
python src/experiment_tracking.py
```
