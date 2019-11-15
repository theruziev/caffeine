FROM python:alpine3.7

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev build-base libffi-dev
RUN pip install --upgrade pip
RUN pip3 install pipenv
RUN set -ex && mkdir /app


WORKDIR /app
COPY ./ /app

# -- Install dependencies:
RUN set -ex && pipenv lock --requirements > requirements.txt && pip3 install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["gunicorn", "caffeine.rest.app:app", "--bind", "0.0.0.0:8000", "--worker-class", "uvicorn.workers.UvicornWorker"]