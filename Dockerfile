FROM public.ecr.aws/lambda/python:3.10

RUN pip install --user --upgrade pip && pip install pipenv==2023.7.3

COPY Pipfile Pipfile.lock ${LAMBDA_TASK_ROOT}

RUN pipenv install --system --deploy

COPY src/lambda_function.py src/model.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]