.PHONY: install dev run lint lint.fix typing fmt fmt.check test build build.docker

install:
	@echo "installing UV"
	if [ ! -d "uv" ]; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
	@echo "installing dependencies"
	uv venv
	uv sync

dev:
	PYTHONPATH=src/ uv run uvicorn 'src.app:app' --host=0.0.0.0 --port=8000 --reload

run:
	uv run uvicorn 'src.app:app' --host=0.0.0.0 --port=8000

lint:
	uv run ruff check
	
lint.fix:
	uv run ruff check --fix

typing:
	uv run pyright --skipunannotated

fmt:
	uv run ruff format

fmt.check:
	uv run ruff format --check --diff

test:
	uv run pytest

build:
	uv build src/

build.docker:
	docker build --platform=linux/amd64 -t backend --output=backend-image .
