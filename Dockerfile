FROM public.ecr.aws/lambda/python:3.10

RUN pip install --user --upgrade pip && pip install pipenv==2023.7.3

COPY Pipfile Pipfile.lock ${LAMBDA_TASK_ROOT}

ENV PIPENV_VERBOSITY -1

RUN pipenv install --system --deploy

COPY streaming/lambda_function.py streaming/model.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
