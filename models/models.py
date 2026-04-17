from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base

SCHEMA = "public"

class Building(Base):
    __tablename__ = "buildings"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    floors = relationship("Floor", back_populates="building")
    grid_points = relationship("GridPoint", back_populates="building")


class Floor(Base):
    __tablename__ = "floors"
    __table_args__ = (
        UniqueConstraint("building_id", "floor_number", name="uq_building_floor"),
        {"schema": SCHEMA}
    )

    id = Column(Integer, primary_key=True, index=True)
    floor_number = Column(Integer, nullable=False)
    building_id = Column(Integer, ForeignKey(f"{SCHEMA}.buildings.id"), nullable=False)

    building = relationship("Building", back_populates="floors")
    grid_points = relationship("GridPoint", back_populates="floor_obj")


class Device(Base):
    __tablename__ = "devices"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(100), unique=True, nullable=False)


class GridPoint(Base):
    __tablename__ = "grid_points"
    __table_args__ = (
        UniqueConstraint("grid_label", "floor_id", name="uq_grid_label_floor"),
        {"schema": SCHEMA}
    )

    id = Column(Integer, primary_key=True, index=True)
    grid_label = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    floor_id = Column(Integer, ForeignKey(f"{SCHEMA}.floors.id"), nullable=False)
    building_id = Column(Integer, ForeignKey(f"{SCHEMA}.buildings.id"), nullable=False)

    floor_obj = relationship("Floor", back_populates="grid_points")
    building = relationship("Building", back_populates="grid_points")


class Beacon(Base):
    __tablename__ = "beacons"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(100), nullable=False)
    major = Column(Integer, nullable=False)
    minor = Column(Integer, nullable=False)


class FingerprintSample(Base):
    __tablename__ = "fingerprint_samples"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    sample_time = Column(TIMESTAMP, server_default=func.now())


class RSSIReading(Base):
    __tablename__ = "rssi_readings"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    sample_id = Column(Integer, ForeignKey(f"{SCHEMA}.fingerprint_samples.id"), nullable=False)
    beacon_id = Column(Integer, ForeignKey(f"{SCHEMA}.beacons.id"), nullable=False)
    rssi_value = Column(Integer)


class PredictedPosition(Base):
    __tablename__ = "predicted_positions"
    __table_args__ = {"schema": SCHEMA}

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey(f"{SCHEMA}.devices.id"), nullable=False)
    grid_point_id = Column(Integer, ForeignKey(f"{SCHEMA}.grid_points.id"), nullable=False)
    predicted_at = Column(TIMESTAMP, server_default=func.now())