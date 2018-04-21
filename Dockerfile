FROM ubuntu:latest

# Enviroment configuration
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    SHELL=/bin/bash

# Install apt-fast
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:apt-fast/stable && \
    apt-get update && \
    apt-get -y install apt-fast

# Install base Python dependencies
RUN apt-fast install -y \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv

# Install Pipfile dependencies
RUN pip3 install --upgrade pip setuptools pipenv

# Install project dependencies
RUN mkdir -p /toodles
WORKDIR /toodles
ADD Pipfile /toodles
RUN pipenv install && pipenv install --dev

EXPOSE 8080
VOLUME ["/toodles"]
