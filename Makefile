# Makefile for Kopi Challenge

.PHONY: help install test run down clean

help:
	@echo "Available make commands:"
	@echo "  make install     Check for Docker and Docker Compose (required)."
	@echo "  make run         Run the service and all related services (API + DB) in Docker."
	@echo "  make test        Run tests (in Docker)."
	@echo "  make down        Teardown of all running services."
	@echo "  make clean       Teardown and removal of all containers and volumes."

install:
	@echo "Checking for Docker and Docker Compose..."
	@if ! command -v docker &> /dev/null; then \
		echo 'Docker not found. Please install Docker: https://docs.docker.com/get-docker/'; \
		exit 1; \
	fi
	@if ! command -v docker-compose &> /dev/null; then \
		echo 'Docker Compose not found. Please install Docker Compose: https://docs.docker.com/compose/install/'; \
		exit 1; \
	fi
	@echo "Docker and Docker Compose are installed."

run:
	docker-compose up --build

down:
	docker-compose down

clean:
	docker-compose down -v

test:
	docker-compose exec app pytest 