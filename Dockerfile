FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-2020-06-06
MAINTAINER Alejandro Macedo

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installing pip-tools for requirements installation
RUN pip install --upgrade pip
RUN pip install pip-tools

# Copying requirements.in to image
COPY requirements.in ./

# Creating requirements.txt
RUN pip-compile

# Installing all dependencies created
RUN pip install -r ./requirements.txt

# Copying application files to the workdir
COPY ./app /app/app