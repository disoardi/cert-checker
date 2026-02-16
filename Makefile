.PHONY: help install test lint format clean build docker-build docker-run tui

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with Poetry
	poetry install

install-dev: ## Install with dev dependencies
	poetry install --with dev

test: ## Run tests
	poetry run pytest tests/ -v --cov=cert_checker --cov-report=term-missing

lint: ## Run linting checks
	poetry run flake8 cert_checker/
	poetry run mypy cert_checker/

format: ## Format code with black
	poetry run black cert_checker/

check: lint test ## Run all checks (lint + test)

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build package
	poetry build

build-binary: ## Build standalone binary with PyInstaller
	poetry run pyinstaller build.spec

docker-build: ## Build Docker image
	docker-compose build

docker-run: ## Run with Docker Compose
	docker-compose up

docker-test: ## Run tests in Docker
	docker run --rm cert-checker pytest

docker-shell: ## Open shell in Docker container
	docker-compose run --rm cert-checker bash

tui: ## Launch TUI with example config
	poetry run cert-checker tui --config config.toml.example

check-google: ## Quick test: check google.com certificate
	poetry run cert-checker check --host google.com --port 443 --verbose

example-config: ## Copy example configuration
	cp config.toml.example config.toml
	@echo "Created config.toml - edit it with your settings"

# Development shortcuts
dev-check: ## Quick check of single host (args: HOST=example.com PORT=443)
	poetry run cert-checker check --host $(or $(HOST),google.com) --port $(or $(PORT),443) -v

dev-list-truststore: ## List example truststore (args: STORE=path/to/store)
	@if [ -z "$(STORE)" ]; then \
		echo "Usage: make dev-list-truststore STORE=path/to/truststore.jks"; \
	else \
		poetry run cert-checker truststore list --store $(STORE) --password changeit; \
	fi

dev-validate: ## Validate certificate (args: CERT=path/to/cert.pem)
	@if [ -z "$(CERT)" ]; then \
		echo "Usage: make dev-validate CERT=path/to/cert.pem"; \
	else \
		poetry run cert-checker validate --cert $(CERT) -v; \
	fi

# Maintenance
update-deps: ## Update dependencies
	poetry update

lock: ## Update lock file
	poetry lock

version: ## Show version
	poetry run cert-checker --version

install-hooks: ## Install git hooks
	@echo "Installing pre-commit hooks..."
	@echo "make format && make lint" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed!"
