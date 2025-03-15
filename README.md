# hse-se-paps
This repository contains implementation lab works

# Tesis

ru: Разработка интеллектуального ассистента программиста

en: development of ai coding assistant


# TO DO
- [x] Initial repository setup
- [x] Lab Work 1 : Requirements
- [x] Lab Work 2 : Architecture design
- [x] Lab Work 3 : Methods and Classes level design
- [x] Lab Work 4 : API
- [x] Lab Work 5 : Docker + 
- [x] Lab Work 6 : Patterns

# Techical stack

- Python 3.13
- FastAPI
- PostgreSQL - database
- ORM
- JWT authentication
- Alembic - db migrations
- UV - python package manager
- VLLM - for llms inference

> Vllm is used to run LLMS on Apple Silicon, docker image was built from source and published on hub. [DOCKER IMAGE](https://hub.docker.com/repository/docker/disk0dancer/vllm-arm).
>
> To run VLLM inference on another platform update [compose.yaml](/compose.yaml).


# Quick start

### 1. Install dependencies

```bash
make install
```

### 2. Run dev

Use local postgres or container, change connection config at `.env`.

```bash
make dev
```

### 3. Run Docker Compose


```bash
docker compose up -d
```

### Check out [Makefile](/Makefile) for more commands and details.
