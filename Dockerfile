FROM python:3.9-alpine
WORKDIR /code
RUN apk add postgresql-dev
COPY requirements.txt /code/
RUN pip install pip setuptools && pip install -r requirements.txt
COPY . /code/

