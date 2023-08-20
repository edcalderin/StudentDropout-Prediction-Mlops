FROM public.ecr.aws/lambda/python:3.10

RUN pip install --user --upgrade pip && pip install pipenv==2023.7.3

COPY Pipfile Pipfile.lock ${LAMBDA_TASK_ROOT}

RUN pipenv install --system --deploy

COPY streaming/*.py ${LAMBDA_TASK_ROOT}
COPY orchestration/*.py orchestration/config.yaml ${LAMBDA_TASK_ROOT}/orchestration/
COPY orchestration/config.yaml ${LAMBDA_TASK_ROOT}/orchestration/config.yaml

COPY data/preprocessed/data_bin.pkl ${LAMBDA_TASK_ROOT}/data/preprocessed/data_bin.pkl

CMD ["lambda_function.lambda_handler"]
