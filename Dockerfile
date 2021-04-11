FROM python:3-alpine

COPY . /app

WORKDIR /app

RUN python3 -m pip install -r requirements.txt --no-cache-dir
