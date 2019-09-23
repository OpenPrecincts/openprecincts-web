OpenPrecincts web application
=============================

[![Build Status](https://travis-ci.com/OpenPrecincts/openprecincts-web.svg?branch=master)](https://travis-ci.com/OpenPrecincts/openprecincts-web)

Docker Usage
------------

Running the project:

    docker-compose up
    # Initialize database by running ./docker/docker-db.sh or set appropriate environment variables.

Updating an image:

    docker-compose build django

Running a management command:

    docker-compose run --rm django /venv/bin/poetry run ./manage.py migrate
