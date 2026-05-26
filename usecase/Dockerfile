FROM python:3.13-slim-bookworm

RUN apt-get update \
  && apt-get dist-upgrade -y \
  && apt-get install -y --no-install-recommends \
    git \
    ssh-client \
    software-properties-common \
    make \
    ca-certificates \
    libpq-dev \
  && apt-get clean \
  && rm -rf \
    /var/lib/apt/lists/* \
    /tmp/* \
    /var/tmp/*

# Env vars
ENV PYTHONIOENCODING=utf-8
ENV LANG=C.UTF-8

WORKDIR /app

# Update python and install
RUN python -m pip install --upgrade pip setuptools wheel --no-cache-dir
COPY dbt/requirements.txt requirements.txt
RUN python -m pip install --no-cache -r requirements.txt

ENV DBT_PROFILES_DIR="/app/dbt"
ENV DBT_PROJECT_DIR="/app/dbt"

COPY . .

WORKDIR /app/dbt/

ENTRYPOINT ["dbt", "run"]

# install dependencies
RUN dbt deps