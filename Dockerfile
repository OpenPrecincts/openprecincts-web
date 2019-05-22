FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1
# based on https://www.caktusgroup.com/blog/2017/03/14/production-ready-dockerfile-your-python-django-app/

RUN mkdir /code/
WORKDIR /code/
ADD . /code/

EXPOSE 8000

RUN BUILD_DEPS=" \
        build-essential \
        libpcre3-dev \
        libpq-dev \
        gdal-bin \
        wget \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS

RUN wget https://deb.nodesource.com/setup_10.x -O nodesource.sh \
    && bash nodesource.sh \
    && apt install -y nodejs \
    && npm ci
    # && npm run build

RUN set -ex \
    && python3.7 -m venv /venv \
    && /venv/bin/pip install -U pip pipenv \
    && /venv/bin/pipenv install
