# Point and Clickle

Guess a point and click adventure game every day

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Black code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

License: MIT

## Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).

## Basic Commands

### Setting up the project

Assuming you are using Docker and docker-compose, you only need to build the containers using the local 
configuration for development.

To build the containers, run:

      $ docker-compose -f local.yml build

Next, you can run the containers using:

      $ docker-compose -f local.yml up -d

Finally, you need to initialize some date by running the following commands:
- Initialize the database
- Create the superuser
- Import the games database
- Filter the imported games

These commands are explained next.

### Initializing database

To initialize the database, run:

      $ python manage.py migrate

.. note::

    If you are using Docker you must run the command above within the django container.:

      $ docker-compose -f local.yml run django python manage.py migrate
    

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "
  Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into
  your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      $ python manage.py createsuperuser

.. note::

    If you are using Docker you must run the command above within the django container.:

      $ docker-compose -f local.yml run django python manage.py createsuperuser

### Importing GamesDB

- To import the games database you need the **gamesdb.json** result of running the scrapper.

- To import the **games database**, use this command:

      $ python manage.py importdb gamesdb.json

.. note::

    If you are using Docker you must run the command above within the django container.:

      $ docker-compose -f local.yml run django python manage.py import gamesdb.json

- Finally you need to filter the database, use this command:

      $ python manage.py filtergames

.. note::

    If you are using Docker you must run the command above within the django container.:

      $ docker-compose -f local.yml run django python manage.py filtergames

### Type checks

Running type checks with mypy:

    $ mypy point_and_clickle

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved
to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading)
.

### Sentry

Sentry is an error logging aggregator service. You can sign up for a free account
at <https://sentry.io/signup/?code=cookiecutter> or download and host it yourself.
The system is set up with reasonable defaults, including 404 logging and integration with the WSGI application.

You must set the DSN url in production.

## Deployment

The following details how to deploy this application.

### Docker

See
detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html)
.
