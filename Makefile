.PHONY: install install-prod generate show serve up down dev-docker dev-k3d-import test lint format clean-cache clean

install:
	uv sync

install-prod:
	uv sync --no-dev

generate:
	uv run gpu-obs data generate --rows 500

show:
	uv run gpu-obs data show

serve:
	uv run sanic gpu_observability.api.main:app --host=0.0.0.0 --port=8000

up:
	docker compose up -d

down:
	docker compose down

build-docker:
	docker build -t gpu-observability:latest .

dev-k3d-import: build-docker
	k3d image import gpu-observability:latest -c $${K3DNAME:-strongwind}

test:
	uv run pytest

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

clean-cache:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

clean: clean-cache
	rm -f data/runs.csv

