from typing import Annotated

from loguru import logger

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session

from api import completions_router, chat_completions_router, healthcheck_router
from services import settings
from src.services.requests_logger import log_request
from src.api.user import router as user_router

app = FastAPI()
app.include_router(completions_router, prefix="/api/v1")
app.include_router(chat_completions_router, prefix="/api/v1")
app.include_router(healthcheck_router, prefix="/api/v1")
app.include_router(user_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _auth(request: Request, call_next):
    response = await call_next(request)
    return response


@app.middleware("http")
async def request_logger_middleware(request: Request, call_next):
    log_request(request)
    response = await call_next(request)
    return response


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    logger.info(f"Settings: {settings}")
    create_db_and_tables()
    # show routes
    logger.info(f"Available endpoints:")
    for route in app.routes:
        logger.info(f"\t{route.path}\tMethods={route.methods}")
