from database import Base as BaseDBModel
from datetime import datetime
from enum import Enum as baseEnum
from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    Uuid,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from sqlalchemy.dialects.postgresql import JSONB
from typing import Any, Optional, List
from typing_extensions import Annotated

int_pk = Annotated[int, mapped_column(Integer, primary_key=True, index=True)]
general_str = Annotated[str, mapped_column(String, nullable=True)]
str_30 = Annotated[str, mapped_column(String(30))]
str_50 = Annotated[str, mapped_column(String(50), nullable=False)]
str_255 = Annotated[str, mapped_column(String(255))]
str_30_indexed_uniq = Annotated[
    str, mapped_column(String(30), nullable=False, index=True, unique=True)
]
str_50_indexed = Annotated[str, mapped_column(String(50), nullable=False, index=True)]
str_26_indexed = Annotated[str, mapped_column(String(26), nullable=False, index=True)]
str_50_indexed_uniq = Annotated[
    str, mapped_column(String(50), nullable=False, index=True, unique=True)
]
str_32_indexed_uniq = Annotated[
    str, mapped_column(String(32), nullable=False, index=True, unique=True)
]
uid_uniq_indexed = Annotated[
    UUID, mapped_column(UUID(as_uuid=True), nullable=False, index=True, unique=True)
]
uuid_36_unique = Annotated[Uuid, mapped_column(Uuid, nullable=False, index=True, unique=True)]
uuid_36 = Annotated[Uuid, mapped_column(Uuid, nullable=False, index=True, unique=False)]
text = Annotated[Text, mapped_column(Text)]
bool_field = Annotated[bool, mapped_column(Boolean, default=False)]


class Base(BaseDBModel):
    pass


class LicensePlate(Base):
    __tablename__ = "license_plate"

    id = mapped_column(Integer, primary_key=True, index=True)
    uuid: Mapped[uuid_36]
    agent_uid: Mapped[str_50] = mapped_column(String, index=True)
    camera_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("camera.id", ondelete="CASCADE"), index=True, nullable=False
    )
    camera: Mapped["Camera"] = relationship("Camera")
    # client_uuid: Mapped[uuid_36] = mapped_column(Uuid, nullable=True, index=True)
    # comment: Mapped[text] = mapped_column(Text, nullable=True)
    # direction_of_travel_degrees: Mapped[int] = mapped_column(Integer, nullable=True)
    live_capture_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    creation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    gps_location = mapped_column(Geometry(geometry_type='POINT', srid=4326, spatial_index=True))
    # plate_image_coordinates: Mapped[List[Any]] = mapped_column(JSONB, nullable=True)
    # plate_number: Mapped[str_50] = mapped_column(String, nullable=False, index=True)
    # agents_group_name: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    region: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    # vehicle_body_type: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    # vehicle_color: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    # vehicle_make: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    # vehicle_make_model: Mapped[str_50] = mapped_column(String, nullable=True, index=True)
    # manually_added: Mapped[bool_field] = mapped_column(Boolean, default=False)
    # hq_vehicle_image: Mapped[str_50] = mapped_column(String, nullable=True)
    # hq_plate_image: Mapped[str_50] = mapped_column(String, nullable=True)
    # lq_vehicle_image: Mapped[str_50] = mapped_column(String, nullable=True)
    # lq_plate_image: Mapped[str_50] = mapped_column(String, nullable=True)
    # hq_vehicle_image_width: Mapped[int] = mapped_column(Integer, nullable=True)
    # hq_vehicle_image_height: Mapped[int] = mapped_column(Integer, nullable=True)


class Camera(Base):
    __tablename__ = "camera"

    id: Mapped[int_pk]
    camera_number: Mapped[str_26_indexed]
    camera_name: Mapped[str_50]
    agent_uid: Mapped[str_50_indexed]
    # nx_cameras_maps: Mapped[List["NxCamerasMap"]] = relationship(
    #     "NxCamerasMap", back_populates="camera"
    # )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# class NxCamerasMap(Base):
#     __tablename__ = "nx_cameras_map"

#     id: Mapped[int_pk]
#     camera_id: Mapped[int] = mapped_column(Integer, ForeignKey("camera.id", ondelete="CASCADE"))
#     camera: Mapped["Camera"] = relationship("Camera", back_populates="nx_cameras_maps")
#     nx_camera_id: Mapped[str_50_indexed]
#     nx_server_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("nx_server.id", ondelete="CASCADE")
#     )
#     nx_server: Mapped["NxServer"] = relationship("NxServer", back_populates="nx_cameras_maps")


# class NxServer(Base):
#     __tablename__ = "nx_server"

#     id: Mapped[int_pk]
#     agent_uid: Mapped[str_50_indexed]
#     system_id: Mapped[str_50_indexed]
#     username: Mapped[str_30]
#     password: Mapped[str_255]
#     nx_cameras_maps: Mapped[List["NxCamerasMap"]] = relationship(
#         "NxCamerasMap", back_populates="nx_server"
#     )
