from fastapi import FastAPI

from core.config.settings import settings
# from apps.core.config.settings import settings
from core.logging.logger import logger

from apps.api.routes.scenario_routes import router as scenario_router



def creat_app():
    app = FastAPI(
        title=settings.APP_NAME,
        description="Supply Chain Decision & Planning Assistant - Scenario Simulation MVP"
    )


    app.include_router(scenario_router)


    @app.get("/")
    async def root():
        logger.info("Root endpoint called")

        return {
            "message": "SC AI Assistant Running",
            "version": "1.0.0",
            "layers": [
                "Interaction Layer (FastAPI)",
                "Orchestration Layer (LangGraph)",
                "Tool/Capability Layer",
                "Recommendation Layer",
                "Memory & Caching Layer",
                "Data Layer (SQLite)",
                "Observability Layer"
            ]
        }


    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.APP_ENV
        }

    return app