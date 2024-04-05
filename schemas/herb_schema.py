from pydantic import BaseModel, ConfigDict, Field, field_validator
from logic.rms_utils import convert_timestamp_to_datetime
from schemas.equipment_schema import EquipmentInDB
from typing import Optional
from datetime import datetime


class HerbBase(BaseModel):
    pass


class HerbCreate(HerbBase):
    uuid: str = Field(alias="herb_uuid")
    harvester_uid: str
    equipment: EquipmentInDB
    harvest_time: datetime = Field(alias="live_capture_timestamp")
    gps_location: str
    region: str
    herb_type: str
    herb_color: str
    herb_image: Optional[str] = None

    model_config = ConfigDict(validate_assignment=True)

    @field_validator('live_capture_time', mode='before')
    def val_live_capture_time(cls, live_capture_timestamp: float) -> datetime:
        return convert_timestamp_to_datetime(live_capture_timestamp)

    def update(self, **new_data):
        for field, value in new_data.items():
            setattr(self, field, value)


class HerbUpdate(HerbBase):
    pass


class HerbInDB(HerbBase):
    id: int
