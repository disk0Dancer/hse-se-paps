.PHONY: install

install:
	@echo "installing UV"
	if [ ! -d "uv" ]; then curl -LsSf https://astral.sh/uv/install.sh | sh; fi
	@echo "installing dependencies"
	uv venv
	uv sync

lint:
	ruff check
	
lint.fix:
	ruff check --fix

typing:
	pyright --skipunannotated --ignoreexternal

fmt:
	ruff format

fmt.check:
	ruff format --check --diff

test:
	pytest
