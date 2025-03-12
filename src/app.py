from loguru import logger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.completions import router as completions_router
from src.api.chat_completions import router as chat_completions_router
from src.api.healthcheck import router as healthcheck_router
from src.api.user import router as user_router
from src.api.auth import router as auth_router

from src.services.settings import settings
from src.models.base import engine, Base


class Application:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Application, cls).__new__(cls)
            app = FastAPI()

            # Chain of Responsibility Pattern
            app.include_router(completions_router, prefix="/api/v1")
            app.include_router(chat_completions_router, prefix="/api/v1")
            app.include_router(healthcheck_router)
            app.include_router(user_router, prefix="/user")
            app.include_router(auth_router)

            # Proxy Pattern
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            # Observer Pattern
            @app.middleware("http")
            async def request_logger_middleware(request: Request, call_next):
                response = await call_next(request)
                return response

            @app.on_event("startup")
            async def on_startup():
                logger.info(f"Settings: {settings.__dict__}")
                # Add specific logging for the Postgres DSN (with password masked)
                pg_dsn = settings.pg_dsn
                masked_dsn = (
                    pg_dsn.replace("postgres:postgres", "postgres:****")
                    if pg_dsn
                    else "Not set"
                )
                logger.info(f"Using PostgreSQL connection string: {masked_dsn}")

                # Create all database tables if they don't exist
                logger.info("Creating database tables if they don't exist...")
                try:
                    async with engine.begin() as conn:
                        # Drop all tables for complete reset - uncomment only if needed
                        # await conn.run_sync(Base.metadata.drop_all)
                        await conn.run_sync(Base.metadata.create_all)
                    logger.info("Database tables created successfully.")
                except Exception as e:
                    logger.error(f"Error creating database tables: {str(e)}")
                    logger.error("Please check your database connection settings.")

                logger.info("Available endpoints:")
                for route in app.routes:
                    logger.info(f"\t{route.path}\tMethods={route.methods}")

            cls._instance.app = app
        return cls._instance


application = Application()
app = application.app
