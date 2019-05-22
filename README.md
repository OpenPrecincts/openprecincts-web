OpenPrecincts web application
=============================

[![Build Status](https://travis-ci.com/OpenPrecincts/openprecincts-web.svg?branch=master)](https://travis-ci.com/OpenPrecincts/openprecincts-web)

Docker Usage
------------

* ``docker-compose up``
* Initialize database by running ``./docker/docker-db.sh`` or set appropriate environment variables.


Local Installation (not recommended)
-------------------------------------

* Install libmagic ``brew install libmagic``
* Install [pipenv](https://pipenv.readthedocs.io/en/latest/)
* ``pipenv install``
* Install [npm](https://www.npmjs.com/)
* ``npm install``
* ``npm run build``
* ``pipenv run ./manage.py migrate``
* ``pipenv run ./manage.py init_data``


Running The Server
-------------------

* ``pipenv run ./manage.py runserver``
* ``npm run start``
