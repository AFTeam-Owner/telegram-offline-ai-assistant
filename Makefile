.PHONY: install dev run test clean docker-build docker-run

# Install dependencies
install:
	pip install -r requirements.txt

# Install with poetry
install-poetry:
	poetry install

# Run in development mode
dev:
	ENV=dev LOG_LEVEL=DEBUG python -m app.main

# Run in production mode
run:
	ENV=prod LOG_LEVEL=INFO python -m app.main

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with coverage
test-cov:
	python -m pytest tests/ -v --cov=app --cov-report=html

# Format code
format:
	black app/ tests/
	isort app/ tests/

# Lint code
lint:
	black --check app/ tests/
	isort --check-only app/ tests/
	flake8 app/ tests/

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Setup development environment
setup:
	mkdir -p storage/uploads storage/chroma storage/logs
	cp sample.env .env
	@echo "Please edit .env file with your API credentials"

# Quick start
start: setup install dev