SERVICE_NAME = recallrai-prototype

.PHONY: all deps database run dev build up down logs shell clean git_pull deploy restart

# ----------Development commands----------
all: dev

deps:
	@echo "Installing dependencies ..."
	poetry install

database:
	@echo "Upgrading database..."
	poetry run alembic upgrade head

run:
	@echo "Running application ..."
	poetry run python3 -m streamlit run main.py
# poetry run python3 -m streamlit run main.py --server.port 8443 --server.sslCertFile=./cert.pem --server.sslKeyFile=./key.pem

# format:
# 	@echo "Formatting code ..."
# 	poetry run black --line-length 100 --skip-string-normalization --skip-magic-trailing-comma --target-version py310 app

dev: deps database run

# ----------Production commands (Docker)----------
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

shell:
	docker compose exec $(SERVICE_NAME) /bin/bash

clean:
	docker compose down -v
	docker system prune -af

git_pull:
	git pull origin main

deploy: down git_pull build up logs
	@echo "Deployment complete"

restart: down up logs
	@echo "Application reloaded"
