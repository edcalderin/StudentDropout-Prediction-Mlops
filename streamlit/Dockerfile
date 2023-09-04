FROM python:3.10-slim

WORKDIR /app

RUN pip install --user --upgrade pip && pip install pipenv==2023.7.3

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY app.py predictions.py ./

ENTRYPOINT [ "streamlit", "run", "app.py"]
