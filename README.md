OpenPrecincts web application
=============================

[![Build Status](https://travis-ci.com/OpenPrecincts/openprecincts-web.svg?branch=master)](https://travis-ci.com/OpenPrecincts/openprecincts-web)

WIP

Installation
---------------

* Install libmagic ``brew install libmagic``
* Install [pipenv](https://pipenv.readthedocs.io/en/latest/)
* ``pipenv install``
* Install [npm](https://www.npmjs.com/)
* ``npm install``
* ``npm run build``
* ``pipenv run ./manage.py migrate``
* ``pipenv run ./manage.py init_data --groups``


Running The Server
-------------------

* ``pipenv run ./manage.py runserver``
* ``npm run start`` (if doing CSS/JS work)
