.PHONY: install dev run lint lint.fix typing fmt fmt.check test build build.docker db.init db.migrate db.upgrade db.downgrade db.history test.postman

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
	PYTHONPATH=src/ uv run uv build

build.docker:
	docker build --platform=linux/amd64 -t backend --output=backend-image .

# Database migration commands
db.init:
	@echo "Initializing alembic"
	PYTHONPATH=. alembic init alembic

db.migrate:
	@echo "Creating migration"
	PYTHONPATH=. alembic revision --autogenerate -m "$(message)"

db.upgrade:
	@echo "Upgrading database to latest version"
	PYTHONPATH=. alembic upgrade head

db.downgrade:
	@echo "Downgrading database by one version"
	PYTHONPATH=. alembic downgrade -1

db.history:
	@echo "Showing migration history"
	PYTHONPATH=. alembic history --verbose

test.postman:
	@echo "Running Postman tests"
	@command -v newman >/dev/null 2>&1 || { echo "Newman is required. Installing..."; npm install -g newman; }
	newman run tests/postman_auth_tests.json
