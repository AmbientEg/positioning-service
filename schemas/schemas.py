from pydantic import BaseModel

class GridPointRequest(BaseModel):
    grid_label: str

class CoordinatesResponse(BaseModel):
    latitude: float
    longitude: float

class GeoJSONImport(BaseModel):
    type: str
    features: list
