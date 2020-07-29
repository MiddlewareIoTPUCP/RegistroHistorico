### Builder ###
FROM python:3.8.1-slim-buster as builder
WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## Installing gcc for wheel compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev

## Upgrading pip and installing pip-tools
RUN pip install --upgrade pip
RUN pip install pip-tools

# Copying requirements.in to image
COPY requirements.in ./

# Creating requirements.txt
RUN pip-compile

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim-2020-06-06

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installing dockerize
RUN apt-get update && apt-get install -y wget
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz


# Copying wheels from builder image
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Copying application files to the workdir
COPY ./app /app/app
