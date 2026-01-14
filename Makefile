#!/bin/bash
# Makefile equivalent for common tasks

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make lint          - Run all linters"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make test          - Run unit tests with coverage"
	@echo "  make security      - Run security checks"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-test   - Test Docker image"
	@echo "  make docker-run    - Run Docker container locally"
	@echo "  make dev           - Start development environment with docker-compose"
	@echo "  make dev-stop      - Stop development environment"
	@echo "  make all           - Run all checks (lint, test, security)"
	@echo "  make clean         - Clean up cache and build artifacts"

.PHONY: install
install:
	@echo "Installing dependencies..."
	poetry install

.PHONY: lint
lint:
	@bash scripts/lint.sh

.PHONY: format
format:
	@bash scripts/format.sh

.PHONY: test
test:
	@echo "Running tests..."
	poetry run pytest tests/ --cov=app --cov-report=html

.PHONY: security
security:
	@bash scripts/security.sh

.PHONY: docker-build
docker-build:
	@bash scripts/docker-test.sh

.PHONY: docker-run
docker-run:
	@docker run -p 8000:8000 \
		-e DATABASE_URL="postgresql://todo_user:todo_password@host.docker.internal:5432/todo_db" \
		todo-api:test

.PHONY: dev
dev:
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "API available at http://localhost:8000"
	@echo "PostgreSQL available at localhost:5432"

.PHONY: dev-stop
dev-stop:
	@echo "Stopping development environment..."
	docker-compose down

.PHONY: all
all: install lint test security
	@echo "All checks passed!"

.PHONY: clean
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .coverage htmlcov/ dist/ build/ *.egg-info
	@echo "Cleanup complete!"
