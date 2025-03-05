.PHONY: install dev run lint lint.fix typing fmt fmt.check test build build.docker

install:
	@echo "installing UV"
	@if [ ! -d "uv" ]; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
	@echo "installing dependencies"
	uv venv
	uv sync

dev:
	PYTHONPATH=src/ uv run uvicorn 'src.app:app' --host=0.0.0.0 --port=8000 --reload

run:
	PYTHONPATH=src/ uv run uvicorn 'src.app:app' --host=0.0.0.0 --port=8000

lint:
	PYTHONPATH=src/ uv run ruff check
	
lint.fix:
	PYTHONPATH=src/ uv run ruff check --fix

typing:
	PYTHONPATH=src/ uv run pyright --skipunannotated

fmt:
	PYTHONPATH=src/ uv run ruff format

fmt.check:
	PYTHONPATH=src/ uv run ruff format --check --diff

test:
	PYTHONPATH=src/ uv run pytest

build:
	PYTHONPATH=src/ uv run uv build src/

build.docker:
	docker build --platform=linux/amd64 -t backend --output=backend-image .
