from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Building, Floor

from core.config import (
    DEFAULT_BUILDING_NAME,
    DEFAULT_BUILDING_DESCRIPTION,
    DEFAULT_FLOOR_NUMBER
)

async def ensure_default_building_and_floor(db: AsyncSession):
    try:
        result = await db.execute(
            select(Building).where(Building.name == DEFAULT_BUILDING_NAME)
        )
        building = result.scalar_one_or_none()

        if not building:
            building = Building(
                name=DEFAULT_BUILDING_NAME,
                description=DEFAULT_BUILDING_DESCRIPTION
            )
            db.add(building)
            await db.flush()

        result = await db.execute(
            select(Floor).where(
                Floor.floor_number == DEFAULT_FLOOR_NUMBER,
                Floor.building_id == building.id
            )
        )
        floor = result.scalar_one_or_none()

        if not floor:
            floor = Floor(
                floor_number=DEFAULT_FLOOR_NUMBER,
                building_id=building.id
            )
            db.add(floor)
            await db.flush()

        await db.commit()
        return building, floor

    except Exception as e:
        await db.rollback()
        raise e