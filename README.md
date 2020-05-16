# PyPSIntegration
[![Build Status](https://travis-ci.org/oriolpiera/dj-icg-prestashop.svg?branch=master)](https://travis-ci.org/oriolpiera/dj-icg-prestashop)
[![codecov](https://codecov.io/gh/oriolpiera/dj-icg-prestashop/branch/master/graph/badge.svg)](https://codecov.io/gh/oriolpiera/dj-icg-prestashop)

## Context

This project was developed previosly with a collection of PHP scripts that you can found here [ICGPrestaShop](https://github.com/oriolpiera/ICGPrestaShop). After a while, it becomes difficult to mantain so I migrate that old code to this new repo a switch to Python using Django framework.

### What is for

This project solve the syncronization of new products (and combinations) including prices and stocks changes. It is only usfull if you have a privative catalan ERP called [ICG Software](https://www.icg.es/en/products/software/) and [Prestashop](https://www.prestashop.com/en) as e-Commerce. This is not an official solution from either of this companies.

### I want to use this with other ERP

No problem, you can implement de **controller.py** and **mssql.py** classes to connect to this other ERP and us other parts of the application to connect to Prestashop.


## Run de tests

```bash
docker-compose build
docker-compose run -e DJANGO_SETTINGS_MODULE=djangodocker.settings.testing --no-deps --rm app bash -c "python manage.py makemigrations; python manage.py migrate; py.test;"
```


#### Original repo used as template: djangodocker

Running Django with Docker step-by-step

This repository stores the changes over the posts about django in docker.

Each post trackes its changes in a different branch:

- [Django development environment with Docker — A step by step guide](https://blog.devartis.com/django-development-environment-with-docker-a-step-by-step-guide-ae234612fa61) - [00-start](https://github.com/devartis/djangodocker/tree/00-start)
- [Django development with Docker — A step by step guide](https://blog.devartis.com/django-development-with-docker-a-step-by-step-guide-525c0d08291) - [01-django-in-docker](https://github.com/devartis/djangodocker/tree/01-django-in-docker)
- [Django development with Docker —A completed development cycle](https://blog.devartis.com/django-development-with-docker-a-completed-development-cycle-7322ad8ba508) - [02-django-development](https://github.com/devartis/djangodocker/tree/02-django-development)
- [Django development with Docker — Testing, Continuous Integration and Docker Hub](https://blog.devartis.com/django-development-with-docker-testing-continuous-integration-and-docker-hub-57038ca19773)

