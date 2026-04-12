ENV ?= dev
ENV_FILE := env/.env.$(ENV)

up:
	docker compose --env-file $(ENV_FILE) up -d --build

down:
	docker compose --env-file $(ENV_FILE) down

restart:
	docker compose --env-file $(ENV_FILE) down
	docker compose --env-file $(ENV_FILE) up -d --build

ps:
	docker compose --env-file $(ENV_FILE) ps

logs:
	docker compose --env-file $(ENV_FILE) logs -f --tail=200

backup:
	./scripts/backup.sh $(ENV)

restore:
	./scripts/restore.sh $(ENV)
