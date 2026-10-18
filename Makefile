# Kuizi developer commands. Run `make help` to list them.
# On Windows, run them inside WSL2 (see docs/dev/local-setup.md).

COMPOSE := docker compose -f infra/local/compose.yaml --env-file .env

.DEFAULT_GOAL := help

.PHONY: help up up-llm down reset status smoke check logs ml-setup ml-lab

help: ## List the commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-10s %s\n", $$1, $$2}'

.env:
	@cp .env.example .env
	@echo "Created .env from .env.example"

up: .env ## Start the local stack and wait until every service is healthy
	$(COMPOSE) up -d --wait
	@$(COMPOSE) run --rm seaweedfs-buckets >/dev/null
	@$(MAKE) --no-print-directory status

up-llm: .env ## Start the stack with the optional LiteLLM gateway
	$(COMPOSE) --profile llm up -d --wait
	@$(COMPOSE) run --rm seaweedfs-buckets >/dev/null
	@$(MAKE) --no-print-directory status

down: ## Stop the stack and keep its data
	$(COMPOSE) --profile llm down

reset: ## Stop the stack, delete all local data, start again from zero
	$(COMPOSE) --profile llm --profile init down -v
	@$(MAKE) --no-print-directory up

status: ## Show each service, its health and its local address
	@$(COMPOSE) --profile llm ps --format 'table {{.Service}}\t{{.Status}}'
	@echo ""
	@. ./.env; echo "PostgreSQL   $$DATABASE_URL"; \
	 echo "Kafka        $$KAFKA_BOOTSTRAP_SERVERS   schema registry $$SCHEMA_REGISTRY_URL"; \
	 echo "Redis        $$REDIS_URL"; \
	 echo "S3           $$S3_ENDPOINT_URL   buckets $$S3_BUCKET_MEDIA, $$S3_BUCKET_ML_ARTIFACTS"; \
	 echo "Keycloak     $$KEYCLOAK_URL/admin   realm $$KEYCLOAK_REALM"; \
	 echo "MLflow       $$MLFLOW_TRACKING_URI"; \
	 echo "LiteLLM      $$LITELLM_URL (only with make up-llm)"

smoke: .env ## Check that every service really works (write and read data)
	@./scripts/smoke-test.sh

check: ## Check the repository is consistent before handing work back
	@python3 scripts/check_repo.py

logs: ## Follow the logs of every service
	$(COMPOSE) --profile llm logs -f --tail=50

ml-setup: ## Install the Python environment for the brain (needs uv)
	cd ml && uv sync

ml-lab: ## Open JupyterLab in the brain environment
	cd ml && uv run jupyter lab
