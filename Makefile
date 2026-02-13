# Makefile for Rule #1 Investing Platform
# Simplifies common Docker operations

.PHONY: help build up down restart logs shell-backend shell-frontend shell-db clean backup restore test

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Rule #1 Investing Platform - Docker Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Usage:$(NC) make [target]"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'

# Setup and Installation
setup: ## Initial setup - copy env file and create directories
	@echo "$(GREEN)Setting up environment...$(NC)"
	@test -f .env || cp .env.example .env
	@mkdir -p backups logs
	@echo "$(GREEN)✓ Setup complete!$(NC)"
	@echo "$(YELLOW)Edit .env file with your API key and settings$(NC)"

# Building
build: ## Build all Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker compose build
	@echo "$(GREEN)✓ Build complete!$(NC)"

build-backend: ## Build only backend image
	@echo "$(GREEN)Building backend image...$(NC)"
	docker compose build backend

build-frontend: ## Build only frontend image
	@echo "$(GREEN)Building frontend image...$(NC)"
	docker compose build frontend

build-no-cache: ## Build all images without cache
	@echo "$(GREEN)Building images without cache...$(NC)"
	docker compose build --no-cache

# Starting and Stopping
up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@echo "$(BLUE)Frontend:$(NC) http://localhost:3000"
	@echo "$(BLUE)Backend:$(NC)  http://localhost:8000"
	@echo "$(BLUE)API Docs:$(NC) http://localhost:8000/api/docs"

up-build: ## Build and start all services
	@echo "$(GREEN)Building and starting all services...$(NC)"
	docker compose up -d --build

up-tools: ## Start all services including pgAdmin
	@echo "$(GREEN)Starting all services with tools...$(NC)"
	docker compose --profile tools up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@echo "$(BLUE)pgAdmin:$(NC)  http://localhost:5050"

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker compose down
	@echo "$(GREEN)✓ Services stopped!$(NC)"

down-volumes: ## Stop all services and remove volumes (⚠️ deletes data!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		echo "$(GREEN)✓ Services stopped and volumes removed!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker compose restart
	@echo "$(GREEN)✓ Services restarted!$(NC)"

restart-backend: ## Restart only backend service
	@echo "$(YELLOW)Restarting backend...$(NC)"
	docker compose restart backend

restart-frontend: ## Restart only frontend service
	@echo "$(YELLOW)Restarting frontend...$(NC)"
	docker compose restart frontend

restart-db: ## Restart only database service
	@echo "$(YELLOW)Restarting database...$(NC)"
	docker compose restart db

# Viewing and Monitoring
ps: ## Show running services
	@docker compose ps

logs: ## View logs from all services
	docker compose logs -f

logs-backend: ## View backend logs
	docker compose logs -f backend

logs-frontend: ## View frontend logs
	docker compose logs -f frontend

logs-db: ## View database logs
	docker compose logs -f db

status: ## Show detailed service status
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(BLUE)Resource Usage:$(NC)"
	@docker stats --no-stream

# Shell Access
shell-backend: ## Open shell in backend container
	@echo "$(BLUE)Opening shell in backend container...$(NC)"
	docker compose exec backend sh

shell-frontend: ## Open shell in frontend container
	@echo "$(BLUE)Opening shell in frontend container...$(NC)"
	docker compose exec frontend sh

shell-db: ## Open PostgreSQL shell
	@echo "$(BLUE)Opening PostgreSQL shell...$(NC)"
	docker compose exec db psql -U postgres -d rule1_investing

# Database Operations
db-init: ## Initialize database tables
	@echo "$(GREEN)Initializing database...$(NC)"
	docker compose exec backend python init_db.py
	@echo "$(GREEN)✓ Database initialized!$(NC)"

db-backup: ## Backup database to backups/ directory
	@echo "$(GREEN)Creating database backup...$(NC)"
	@mkdir -p backups
	docker compose exec -T db pg_dump -U postgres rule1_investing > "backups/backup_$$(date +%Y%m%d_%H%M%S).sql"
	@echo "$(GREEN)✓ Backup created in backups/ directory$(NC)"

db-restore: ## Restore database from backup (specify FILE=path/to/backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: Please specify FILE=path/to/backup.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	@cat $(FILE) | docker compose exec -T db psql -U postgres -d rule1_investing
	@echo "$(GREEN)✓ Database restored!$(NC)"

db-reset: ## Reset database (⚠️ deletes all data!)
	@echo "$(RED)WARNING: This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v; \
		docker compose up -d db; \
		sleep 5; \
		docker compose up -d backend; \
		echo "$(GREEN)✓ Database reset complete!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

# Cleaning
clean: ## Remove stopped containers and unused images
	@echo "$(YELLOW)Cleaning up Docker resources...$(NC)"
	docker compose down
	docker system prune -f
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

clean-all: ## Remove all containers, images, and volumes (⚠️ deletes everything!)
	@echo "$(RED)WARNING: This will delete all Docker resources for this project!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v --rmi all; \
		docker system prune -af --volumes; \
		echo "$(GREEN)✓ All resources removed!$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled.$(NC)"; \
	fi

# Production
prod-up: ## Start production stack
	@echo "$(GREEN)Starting production stack...$(NC)"
	docker compose -f docker compose.prod.yml up -d
	@echo "$(GREEN)✓ Production services started!$(NC)"

prod-down: ## Stop production stack
	@echo "$(YELLOW)Stopping production stack...$(NC)"
	docker compose -f docker compose.prod.yml down

prod-logs: ## View production logs
	docker compose -f docker compose.prod.yml logs -f

prod-build: ## Build production images
	@echo "$(GREEN)Building production images...$(NC)"
	docker compose -f docker compose.prod.yml build

# Testing
test-backend: ## Run backend tests
	@echo "$(BLUE)Running backend tests...$(NC)"
	docker compose exec backend pytest

test-api: ## Test API health
	@echo "$(BLUE)Testing API endpoints...$(NC)"
	@curl -f http://localhost:8000/ && echo "$(GREEN)✓ API is healthy!$(NC)" || echo "$(RED)✗ API is down!$(NC)"

# Development
dev: setup up ## Setup and start development environment
	@echo "$(GREEN)Development environment ready!$(NC)"

# Quick commands
quick-restart: down up ## Quick restart (down + up)
	@echo "$(GREEN)Quick restart complete!$(NC)"

quick-logs: ## Tail logs from all services
	@docker compose logs -f --tail=50
