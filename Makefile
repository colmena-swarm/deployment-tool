# Makefile for COLMENA Deployment Tool

.PHONY: help install install-dev test test-unit test-integration test-coverage clean lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	pip install .

install-dev: ## Install the package with development dependencies
	pip install -e ".[test]"

test: ## Run all tests
	pytest

test-unit: ## Run unit tests only
	pytest -m unit

test-integration: ## Run integration tests only
	pytest -m integration

test-coverage: ## Run tests with coverage report
	pytest --cov=deployment --cov-report=html --cov-report=term-missing

clean: ## Clean up generated files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint: ## Run linting (if you add flake8 or similar)
	@echo "Linting not configured yet"

format: ## Format code (if you add black or similar)
	@echo "Code formatting not configured yet"

docker-test: ## Run tests in Docker container
	docker build -t deployment-tool-test .
	docker run --rm deployment-tool-test pytest

ci-test: ## Run tests for CI (no interactive output)
	pytest --tb=short --cov=deployment --cov-report=xml
