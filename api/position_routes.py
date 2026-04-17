from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import json

from database.database import get_db_session
from schemas.schemas import GridPointRequest, CoordinatesResponse
from services.position_service import PositionService
from utils.db_utils import ensure_default_building_and_floor
from utils.file_utils import extract_rssi_from_file

router = APIRouter()


# ---------------------------------------------------
# API 1
# Get coordinates from gridpoint
# ---------------------------------------------------

@router.post("/grid/coordinates", response_model=CoordinatesResponse)
async def get_coordinates(
    request: GridPointRequest,
    db: AsyncSession = Depends(get_db_session)
):
    try:
        result = await PositionService.get_coordinates(request.grid_label, db)

        if not result:
            raise HTTPException(status_code=404, detail="Grid point not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------
# API 2
# Import GeoJSON gridpoints
# ---------------------------------------------------

@router.post("/grid/import")
async def import_gridpoints(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):

    await ensure_default_building_and_floor(db)

    content = await file.read()
    geojson = json.loads(content)

    inserted = await PositionService.import_geojson(geojson, db)

    return {
        "message": "Gridpoints imported successfully",
        "count": inserted
    }


# ---------------------------------------------------
# API 3 — Predict grid from RSSI
# ---------------------------------------------------

@router.post("/predict")
async def predict(
    request: Request,
    files: list[UploadFile] = File(...)
):
    try:
        if len(files) != 5:
            raise HTTPException(
                status_code=400,
                detail="Exactly 5 beacon files required"
            )

        beacon_data = [
            extract_rssi_from_file(file)
            for file in files
        ]

        min_len = min(len(v) for v in beacon_data)

        if min_len < 20:
            raise HTTPException(
                status_code=400,
                detail="Not enough samples (minimum 20 required)"
            )

        rssi_matrix = np.array([b[:min_len] for b in beacon_data])

        cnn_service = request.app.state.cnn_service
        predicted_grid = cnn_service.predict(rssi_matrix)

        return {"predicted_grid": str(predicted_grid)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))