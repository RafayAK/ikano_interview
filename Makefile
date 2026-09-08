.DEFAULT_GOAL := help

COMPOSE ?= docker compose
UV ?= uv
NPM ?= npm
DB_PORT ?= 5432
BACKEND_PORT ?= 8000
FRONTEND_PORT ?= 4321
export DB_PORT BACKEND_PORT FRONTEND_PORT

.PHONY: help up down logs ps db-up db-down install dev backend frontend frontend-stop frontend-logs test build

help: ## Show available commands (run from the repository root)
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Build and start the full Docker stack; wait until healthy
	$(COMPOSE) up --build --wait

down: ## Stop the Docker stack, preserving database data
	$(COMPOSE) down

logs: ## Follow Docker logs (optionally: make logs SERVICE=backend)
	$(COMPOSE) logs --follow $(SERVICE)

ps: ## Show Docker service status
	$(COMPOSE) ps

db-up: ## Start only Postgres for local development
	$(COMPOSE) up --wait db

db-down: ## Stop Postgres, preserving database data
	$(COMPOSE) stop db

install: ## Install local backend and frontend dependencies from lockfiles
	cd backend && $(UV) sync --locked
	cd frontend && $(NPM) ci

dev: ## Run both apps locally with live reload (Ctrl-C stops both)
	@trap 'kill 0' EXIT INT TERM; \
	(cd frontend && PUBLIC_API_BASE_URL="http://localhost:$(BACKEND_PORT)/api/v1" $(NPM) run dev -- --port $(FRONTEND_PORT)) & \
	(cd backend && $(UV) run uvicorn app.main:app --reload --port $(BACKEND_PORT))

backend: ## Run the local API with reload (foreground)
	cd backend && $(UV) run uvicorn app.main:app --reload --port $(BACKEND_PORT)

frontend: ## Start the local UI in the background
	cd frontend && PUBLIC_API_BASE_URL="$${PUBLIC_API_BASE_URL:-http://localhost:$(BACKEND_PORT)/api/v1}" $(NPM) run dev -- --background --port $(FRONTEND_PORT)

frontend-stop: ## Stop the local background UI
	cd frontend && $(NPM) run dev -- stop

frontend-logs: ## Follow local UI logs
	cd frontend && $(NPM) run dev -- logs --follow

test: ## Run backend tests (Docker required for disposable test Postgres)
	cd backend && $(UV) run pytest $(ARGS)

build: ## Build the frontend locally
	cd frontend && $(NPM) run build

build-prod: ## Build the unified multi-stage production Docker image
	docker build -f prod.Dockerfile -t ikano-app:latest .

# --- Decoupled Deployment Pipeline ---

ecr-init: ## Initialize pre-app ECR Terraform
	terraform -chdir=terraform/global/ecr init

ecr-apply: ## Provision pre-app ECR repository
	terraform -chdir=terraform/global/ecr apply

build-push: ## Authenticate to ECR, build production image, and push
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $$(terraform -chdir=terraform/global/ecr output -raw repository_url)
	docker build -f prod.Dockerfile -t $$(terraform -chdir=terraform/global/ecr output -raw repository_url):latest .
	docker push $$(terraform -chdir=terraform/global/ecr output -raw repository_url):latest

app-init: ## Initialize app hosting Terraform (VPC, RDS, ALB, ECS)
	terraform -chdir=terraform/live/dev init

app-plan: ## Run Terraform plan for app hosting
	terraform -chdir=terraform/live/dev plan

app-apply: ## Apply Terraform app hosting (ECS will immediately pull pre-existing image)
	terraform -chdir=terraform/live/dev apply

app-output: ## Show Terraform app hosting outputs (ALB URL, RDS, etc.)
	terraform -chdir=terraform/live/dev output

deploy: ## Full deployment sequence: ECR -> Build & Push -> App Infra
	@echo "==> Step 1: Provisioning pre-app ECR repository..."
	terraform -chdir=terraform/global/ecr apply -auto-approve
	@echo "==> Step 2: Building and pushing container image to ECR..."
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $$(terraform -chdir=terraform/global/ecr output -raw repository_url)
	docker build -f prod.Dockerfile -t $$(terraform -chdir=terraform/global/ecr output -raw repository_url):latest .
	docker push $$(terraform -chdir=terraform/global/ecr output -raw repository_url):latest
	@echo "==> Step 3: Provisioning app hosting infrastructure..."
	terraform -chdir=terraform/live/dev apply -auto-approve
	@echo "==> Deployment complete! Open the ALB URL below:"
	@terraform -chdir=terraform/live/dev output alb_url

app-destroy: ## Tear down app hosting infrastructure
	terraform -chdir=terraform/live/dev destroy

ecr-destroy: ## Tear down ECR repository
	terraform -chdir=terraform/global/ecr destroy

destroy-all: ## Tear down everything (App + ECR) for clean 1-week teardown
	terraform -chdir=terraform/live/dev destroy
	terraform -chdir=terraform/global/ecr destroy

# Aliases for backward compatibility
tf-init: app-init
tf-plan: app-plan
tf-apply: app-apply
tf-destroy: app-destroy
tf-output: app-output
