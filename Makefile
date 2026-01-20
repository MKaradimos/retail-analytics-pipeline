.PHONY: help setup build up down run logs clean test

help:
	@echo "Retail Analytics Pipeline - Available Commands"
	@echo "=============================================="
	@echo "make setup      - Initial setup (generate sample data, create .env)"
	@echo "make build      - Build Docker images"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make run        - Run pipeline manually"
	@echo "make logs       - View pipeline logs"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make test       - Run tests"
	@echo "make shell      - Open shell in pipeline container"
	@echo "make psql       - Connect to PostgreSQL database"

setup:
	@echo "Setting up project..."
	@cp .env.example .env
	@python data/generate_sample_data.py
	@echo "✓ Setup complete!"

build:
	@echo "Building Docker images..."
	@docker-compose build

up:
	@echo "Starting services..."
	@docker-compose up -d
	@echo "✓ Services started!"
	@echo "PostgreSQL: localhost:5432"
	@echo "pgAdmin: http://localhost:5050"

down:
	@echo "Stopping services..."
	@docker-compose down

run:
	@echo "Running pipeline..."
	@docker-compose run --rm pipeline python pipeline.py

logs:
	@docker-compose logs -f pipeline

clean:
	@echo "Cleaning up..."
	@docker-compose down -v
	@rm -rf logs/*.log
	@echo "✓ Cleanup complete!"

test:
	@echo "Running tests..."
	@docker-compose run --rm pipeline pytest

shell:
	@docker-compose run --rm pipeline /bin/bash

psql:
	@docker-compose exec postgres psql -U analytics_user -d retail_analytics

# Quick start for new users
quickstart: setup build up
	@echo ""
	@echo "✓ Quick start complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Run 'make run' to execute the pipeline"
	@echo "  2. Access pgAdmin at http://localhost:5050"
	@echo "  3. Run analytics queries from sql/analytics_queries.sql"
