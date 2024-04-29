from database import Base as BaseDBModel
from datetime import datetime
from geoalchemy2 import Geometry
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Uuid,
)
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]
uuid_36 = Annotated[Uuid, mapped_column(Uuid, nullable=False, index=True, unique=False)]
str_50 = Annotated[str, mapped_column(String(50), nullable=False)]
str_26_indexed = Annotated[str, mapped_column(String(26), nullable=False, index=True)]
str_50_indexed = Annotated[str, mapped_column(String(50), nullable=False, index=True, unique=True)]


class Base(BaseDBModel):
    def get_harvester_uid(self, db, model_id):
        return None


class Herb(Base):
    __tablename__ = "herb"

    id = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[uuid_36]
    harvester_uid: Mapped[str_50_indexed] = mapped_column(String, index=True)
    equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("equipment.id", ondelete="CASCADE"), index=True, nullable=False
    )
    equipment: Mapped["Equipment"] = relationship("Equipment")
    harvest_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    gps_location = mapped_column(Geometry(geometry_type='POINT', srid=4326, spatial_index=True))
    region: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    herb_type: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    herb_color: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    herb_image: Mapped[int] = mapped_column(Integer, nullable=True)

    def get_harvester_uid(self, db, model_id):
        return db.query(Herb.harvester_uid).filter(Herb.id == model_id).scalar()

class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[int_pk]
    number: Mapped[str_26_indexed]
    name: Mapped[str_50]
    harvester_uid: Mapped[str_50_indexed]
    project_uuid: Mapped[uuid_36] = mapped_column(Uuid, index=True)
    company_uuid: Mapped[uuid_36] = mapped_column(Uuid, index=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def field_value_to_str(self, field_name: str) -> str:
        return str(getattr(self, field_name))
    
    def get_harvester_uid(self, db, model_id):
        return db.query(Equipment.harvester_uid).filter(Equipment.id == model_id).scalar()
