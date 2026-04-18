.PHONY: help install dev run lint format typecheck test build clean

help:
	@echo "nimbus — Production-Grade Dynamic Island for Windows"
	@echo ""
	@echo "Targets:"
	@echo "  make install      Install package in production mode"
	@echo "  make dev          Install package + dev dependencies in editable mode"
	@echo "  make run          Run the nimbus application"
	@echo "  make lint         Run ruff linter"
	@echo "  make format       Format code with ruff"
	@echo "  make typecheck    Type-check with mypy"
	@echo "  make test         Run pytest test suite"
	@echo "  make build        Build distribution packages"
	@echo "  make clean        Remove build artifacts"

install:
	- pip install -e .

dev:
	- pip install -e ".[dev]"

run:
	- python -m nimbus

lint:
	- ruff check nimbus/ tests/

format:
	- ruff format nimbus/ tests/

typecheck:
	- mypy nimbus/

test:
	- pytest

build:
	- python -m build

clean:
	- rm -rf build/ dist/ *.egg-info/
	- find . -type d -name __pycache__ -exec rm -rf {} +
	- find . -type f -name "*.pyc" -delete
	- find . -type d -name "*.egg-info" -exec rm -rf {} +
	