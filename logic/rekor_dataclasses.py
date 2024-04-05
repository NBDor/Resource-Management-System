from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Optional, List
from config.constants import DEFAULT_MIN_PLATE_LEN, CAMERA_ID

from log.logger import logger as logging


class Candidate(BaseModel):
    plate: str
    confidence: float
    matches_template: int


class Coordinate(BaseModel):
    x: int
    y: int


class VehicleRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int


class BestPlate(BaseModel):
    plate: str
    confidence: float
    matches_template: int
    plate_index: int
    region: str
    region_confidence: float
    processing_time_ms: float
    requested_topn: int
    coordinates: List[Coordinate]
    plate_crop_jpeg: Optional[str] = None
    vehicle_region: VehicleRegion
    vehicle_detected: bool
    candidates: List[Candidate]


class VehicleSpecification(BaseModel):
    name: str
    confidence: float


class Vehicle(BaseModel):
    vehicle_color: List[VehicleSpecification] = Field(alias="color")
    vehicle_make: List[VehicleSpecification] = Field(alias="make")
    vehicle_make_model: List[VehicleSpecification] = Field(alias="make_model")
    vehicle_body_type: List[VehicleSpecification] = Field(alias="body_type")
    year: List[VehicleSpecification]
    orientation: List[VehicleSpecification]

    @field_validator("vehicle_body_type", "vehicle_color", "vehicle_make")
    @classmethod
    def get_first_vehicle_spec_name(cls, vehicle_spec: List[VehicleSpecification]) -> str:
        return vehicle_spec[0].name

    @field_validator("vehicle_make_model")
    @classmethod
    def get_first_make_model_name(cls, make_model: List[VehicleSpecification]) -> str:
        return make_model[0].name.replace("_", " ")


class AgentConfiguration(BaseModel):
    brand: str
    min_plate_len: Optional[int] = DEFAULT_MIN_PLATE_LEN


class RekorALPR(BaseModel):
    data_type: str
    version: int
    live_capture_timestamp: float = Field(alias="epoch_start")
    epoch_end: int
    frame_start: int
    frame_end: int
    company_id: str
    agent_uid: str
    agent_version: str
    agent_type: str
    camera_number: str = Field(alias=CAMERA_ID)
    user_data: Optional[str] = None
    client_uuid: str
    agents_group_name: str
    gps_latitude: float
    gps_longitude: float
    country: str
    uuids: List[str]
    plate_indexes: List[int]
    candidates: List[Candidate]
    vehicle_crop_jpeg: Optional[str] = None
    best_plate: BestPlate
    best_confidence: float
    license_plate_uuid: str = Field(alias="best_uuid")
    best_plate_number: str
    best_region: str
    best_region_confidence: float
    matches_template: bool
    best_image_width: int
    best_image_height: int
    travel_direction: float
    is_parked: bool
    is_preview: bool
    vehicle: Vehicle

    # Extra Fields:
    agent_configuration: AgentConfiguration

    @field_validator("live_capture_timestamp", mode="before")
    @classmethod
    def normalize_live_capture_timestamp(cls, live_capture_time: float) -> float:
        return live_capture_time / 1e3

    @computed_field
    @property
    def gps_location(self) -> str:
        return f"POINT({self.gps_longitude} {self.gps_latitude})"

    @model_validator(mode="after")
    def best_plate_number_must_be_greater_than_configured_min_plate_len_value(
        self,
    ) -> "RekorALPR":
        if self.user_data and self.agents_group_name != self.user_data:
            log_message = "Wrong agents group name - check your agent configuration"
            logging.error(
                f"{log_message} | Agent: {self.agent_uid} | Request: '{self.user_data}' | DB: '{self.agents_group_name}'"
            )
            raise ValueError(log_message)

        if len(self.best_plate_number) < self.agent_configuration.min_plate_len:
            raise ValueError("License Plate filtered out due to length validation")
        return self
