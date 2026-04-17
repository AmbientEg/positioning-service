from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.models import GridPoint
from utils.db_utils import ensure_default_building_and_floor


class PositionService:

    @staticmethod
    async def get_coordinates(grid_label: str, db: AsyncSession):
        try:
            result = await db.execute(
                select(GridPoint).where(GridPoint.grid_label == str(grid_label))
            )
            grid = result.scalar_one_or_none()

            if not grid:
                return None

            return {
                "latitude": grid.latitude,
                "longitude": grid.longitude
            }

        except Exception as e:
            raise e

    @staticmethod
    async def import_geojson(geojson: dict, db: AsyncSession):
        try:
            features = geojson.get("features", [])
            inserted_count = 0

            building, floor = await ensure_default_building_and_floor(db)

            for feature in features:
                try:
                    properties = feature.get("properties", {})
                    geometry = feature.get("geometry", {})
                    coordinates = geometry.get("coordinates")

                    if not coordinates:
                        continue

                    if isinstance(coordinates[0], list):
                        coordinates = coordinates[0]

                    if len(coordinates) < 2:
                        continue

                    longitude = float(coordinates[0])
                    latitude = float(coordinates[1])

                    grid_label = properties.get("grid_id")
                    if grid_label is None:
                        continue

                    grid_label = str(grid_label)

                    existing = await db.execute(
                        select(GridPoint).where(GridPoint.grid_label == grid_label)
                    )
                    if existing.scalar_one_or_none():
                        continue

                    grid = GridPoint(
                        grid_label=grid_label,
                        latitude=latitude,
                        longitude=longitude,
                        floor_id=floor.id,
                        building_id=building.id
                    )

                    db.add(grid)
                    inserted_count += 1

                except Exception:
                    continue

            await db.commit()
            return {"inserted": inserted_count}

        except Exception as e:
            await db.rollback()
            raise e