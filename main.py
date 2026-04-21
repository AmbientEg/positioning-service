import logging
import os
import time
import uuid
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import position_routes
from database.database import engine

from DeepLearningModel.loader import ModelLoader
from services.cnn_service import CNNService


SERVICE_NAME = "positioning-service"
SERVICE_VERSION = "1.0.0"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
STARTED_AT = datetime.now(timezone.utc)


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(SERVICE_NAME)


app = FastAPI(
    title="Positioning Service",
    description="Positioning Service",
    version=SERVICE_VERSION,
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not IS_PRODUCTION else None,
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name,
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "tryItOutEnabled": True,
        "persistAuthorization": True,
    }
)

# ---------------------------
# Load ML model ONCE at startup
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Loader = ModelLoader(
    model_path=os.path.join(BASE_DIR, "DeepLearningModel", "ble_position_model.onnx"),
    scaler_path=os.path.join(BASE_DIR, "DeepLearningModel", "scaler.pkl"),
    mapping_path=os.path.join(BASE_DIR, "DeepLearningModel", "label_mapping.pkl"),
)

cnn_service = CNNService(Loader)

# Attach service to app (clean access inside routes)
app.state.cnn_service = cnn_service


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "unhandled request failure request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000, 2)
    response.headers["x-request-id"] = request_id

    logger.info(
        "request completed request_id=%s method=%s path=%s status=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response


app.include_router(
    position_routes.router,
    prefix="/position",
    tags=["Positioning"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("x-request-id", "")
    logger.exception(
        "internal server error request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    detail = str(exc) if not IS_PRODUCTION else "Internal server error"

    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": detail,
            "request_id": request_id,
        }
    )


async def check_database() -> tuple[str, str | None]:
    try:
        async with engine.connect() as connection:
            await connection.exec_driver_sql("SELECT 1")
        return "up", None
    except Exception as exc:
        return "down", str(exc)


def uptime_seconds() -> int:
    return int((datetime.now(timezone.utc) - STARTED_AT).total_seconds())

# ----------------------------------------------------
# Production Health and Monitoring Endpoints
# ----------------------------------------------------
@app.get("/health/live")
async def health_live():
    return {
        "status": "alive",
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "version": SERVICE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds(),
    }


@app.get("/health/ready")
async def health_ready():
    db_status, db_detail = await check_database()
    model_ready = hasattr(app.state, "cnn_service")

    health_payload = {
        "status": "healthy" if db_status == "up" and model_ready else "unhealthy",
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "version": SERVICE_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds(),
        "checks": {
            "database": db_status,
            "model": "up" if model_ready else "down",
        }
    }

    if db_detail and not IS_PRODUCTION:
        health_payload["checks"]["database_detail"] = db_detail

    if health_payload["status"] == "healthy":
        return health_payload

    return JSONResponse(status_code=503, content=health_payload)


@app.get("/health")
async def health_check():
    return await health_ready()

@app.get("/")
async def root():
    return {
        "message": "Positioning Service is running",
        "version": SERVICE_VERSION,
        "environment": ENVIRONMENT,
        "documentation": "/docs" if not IS_PRODUCTION else None,
        "health": "/health",
        "liveness": "/health/live",
        "readiness": "/health/ready",
        "endpoints": {
            "import_grid": "/position/grid/import",
            "predict": "/position/predict"
        }
    }