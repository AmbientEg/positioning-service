from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import position_routes

from DeepLearningModel.loader import ModelLoader
from services.cnn_service import CNNService
import os

app = FastAPI(title="Positioning Service")

# ---------------------------
# Load ML model ONCE at startup
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

Loader = ModelLoader(
    model_path=os.path.join(BASE_DIR, "DeepLearningModel", "ble_position_model.h5"),
    scaler_path=os.path.join(BASE_DIR, "DeepLearningModel", "scaler.pkl"),
    mapping_path=os.path.join(BASE_DIR, "DeepLearningModel", "label_mapping.pkl"),
)

cnn_service = CNNService(Loader)

# Attach service to app (clean access inside routes)
app.state.cnn_service = cnn_service


app.include_router(
    position_routes.router,
    prefix="/position",
    tags=["Positioning"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc)
        }
    )