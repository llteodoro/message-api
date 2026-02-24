.PHONY: help install test lint docker-build docker-run docker-stop docker-logs docker-push clean all

# Variables
PYTHON := python3
PIP := pip3
DOCKER_REGISTRY ?= ghcr.io
DOCKER_ORG ?= $(shell git config --get user.name | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
IMAGE_NAME ?= message-api
IMAGE_VERSION ?= latest
IMAGE_TAG := $(DOCKER_REGISTRY)/$(DOCKER_ORG)/$(IMAGE_NAME):$(IMAGE_VERSION)

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m

help: ## Show available commands
	@echo "$(GREEN)Message API - Development & Docker Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

## Development
install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt

dev: ## Run development server with reload
	@echo "$(GREEN)Starting development server...$(NC)"
	$(PYTHON) -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	@echo "$(GREEN)Running tests...$(NC)"
	$(PYTHON) -m pytest tests/ -v --cov=app --cov-report=html

test-fast: ## Run tests without coverage
	@echo "$(GREEN)Running tests (fast)...$(NC)"
	$(PYTHON) -m pytest tests/ -v

lint: ## Run linting checks
	@echo "$(GREEN)Running linting...$(NC)"
	flake8 app tests --max-line-length=120 || true
	black --check app tests || true

format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	black app tests

## Docker Commands
docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image: $(IMAGE_TAG)$(NC)"
	docker build -t $(IMAGE_TAG) .
	@echo "$(GREEN)✓ Built: $(IMAGE_TAG)$(NC)"

docker-run: docker-build ## Build and run Docker container
	@echo "$(GREEN)Running container...$(NC)"
	docker run -d -p 8000:8000 \
		--name message-api \
		-e LOG_LEVEL=INFO \
		$(IMAGE_TAG)
	@echo "$(GREEN)✓ Running at http://localhost:8000$(NC)"

docker-stop: ## Stop running container
	@echo "$(GREEN)Stopping container...$(NC)"
	docker stop message-api && docker rm message-api || true

docker-logs: ## View container logs
	docker logs -f message-api

docker-push: docker-build ## Push Docker image to registry
	@echo "$(GREEN)Pushing to $(DOCKER_REGISTRY)...$(NC)"
	docker tag $(IMAGE_TAG) $(DOCKER_REGISTRY)/$(DOCKER_ORG)/$(IMAGE_NAME):latest
	docker push $(IMAGE_TAG)
	docker push $(DOCKER_REGISTRY)/$(DOCKER_ORG)/$(IMAGE_NAME):latest
	@echo "$(GREEN)✓ Pushed successfully$(NC)"

docker-compose-up: ## Start services with docker-compose
	@echo "$(GREEN)Starting services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services running$(NC)"

docker-compose-down: ## Stop services
	@echo "$(GREEN)Stopping services...$(NC)"
	docker-compose down

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

## Testing
test-health: ## Test API health endpoint
	@echo "$(GREEN)Testing health endpoint...$(NC)"
	curl -s http://localhost:8000/health && echo "" || echo "Failed"

test-api: ## Test API endpoints
	@echo "$(GREEN)Testing API endpoints...$(NC)"
	@curl -s -X POST http://localhost:8000/messages \
		-H "Content-Type: application/json" \
		-d '{"text": "Test message"}' | $(PYTHON) -m json.tool || echo "{}"; \
	curl -s http://localhost:8000/messages | $(PYTHON) -m json.tool || echo "[]"; \
	curl -s http://localhost:8000/metrics | $(PYTHON) -m json.tool || echo "{}"

## Utility
clean: ## Clean up generated files
	@echo "$(GREEN)Cleaning...$(NC)"
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '.pytest_cache' -delete
	rm -rf htmlcov/ dist/ build/ *.egg-info

all: clean install test docker-build ## Run full pipeline
	@echo "$(GREEN)✓ Full pipeline complete$(NC)"

version: ## Show version info
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Image Tag: $(IMAGE_TAG)"

.DEFAULT_GOAL := help
