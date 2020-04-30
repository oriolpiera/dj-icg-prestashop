# PyPSIntegration
[![Build Status](https://travis-ci.org/oriolpiera/dj-icg-prestashop.svg?branch=master)](https://travis-ci.org/oriolpiera/dj-icg-prestashop)
[![codecov](https://codecov.io/gh/oriolpiera/dj-icg-prestashop/branch/master/graph/badge.svg)](https://codecov.io/gh/oriolpiera/dj-icg-prestashop)

## Run de tests

```bash
docker-compose build
docker-compose run -e DJANGO_SETTINGS_MODULE=djangodocker.settings.testing --no-deps --rm app bash -c "python manage.py makemigrations; python manage.py migrate; py.test;"
```


## Original repo used as template: djangodocker

Running Django with Docker step-by-step

This repository stores the changes over the posts about django in docker.

Each post trackes its changes in a different branch:

- [Django development environment with Docker — A step by step guide](https://blog.devartis.com/django-development-environment-with-docker-a-step-by-step-guide-ae234612fa61) - [00-start](https://github.com/devartis/djangodocker/tree/00-start)
- [Django development with Docker — A step by step guide](https://blog.devartis.com/django-development-with-docker-a-step-by-step-guide-525c0d08291) - [01-django-in-docker](https://github.com/devartis/djangodocker/tree/01-django-in-docker)
- [Django development with Docker —A completed development cycle](https://blog.devartis.com/django-development-with-docker-a-completed-development-cycle-7322ad8ba508) - [02-django-development](https://github.com/devartis/djangodocker/tree/02-django-development)
- [Django development with Docker — Testing, Continuous Integration and Docker Hub](https://blog.devartis.com/django-development-with-docker-testing-continuous-integration-and-docker-hub-57038ca19773)

