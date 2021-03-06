FROM python:3.7

ARG requirements=requirements/production.txt
ENV DJANGO_SETTINGS_MODULE=djangodocker.settings.production

#Set de locale
ENV LC_ALL es_ES.UTF-8

WORKDIR /app

COPY djangodocker djangodocker
COPY manage.py /app/
COPY requirements/ /app/requirements/ 

RUN pip install -r $requirements

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]

