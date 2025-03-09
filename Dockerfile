ARG PYTHON_VERSION=3.13
ARG UV_VERSION=0.5.24

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev gcc
COPY --from=uv /uv /uvx /bin/
WORKDIR /app

ADD src/ src/
ADD uv.lock uv.lock
ADD pyproject.toml pyproject.toml

RUN uv sync --frozen
EXPOSE 8000

CMD uv run uvicorn 'src.app:app' --host=0.0.0.0 --port=8000
