dco-up:
	 docker-compose up -d

dco-rm:
	 docker-compose down
	 docker-compose rm -f

install:
	pipenv install
	pipenv install -e .

migrate:
	 pipenv run alembic upgrade head

migrate-sql:
	 pipenv run alembic upgrade head --sql

lint:
	pipenv run black -l 100 --check caffeine tests scripts
	pipenv run flake8 caffeine scripts

format:
	pipenv run black -l 100 caffeine/ tests/

run: dco-up
	 uvicorn caffeine.rest.app:app --reload --lifespan on

test: dco-up migrate
	 pipenv run pytest tests

test-parallel: dco-up migrate
	 pipenv run pytest tests -n auto

app-version:
	 ./scripts/version


