from pydantic import BaseModel, Field, field_validator, model_validator, computed_field
from typing import Optional, List
from config.constants import DEFAULT_MIN_CHEMICAL_ANALYSIS_VALUE

from log.logger import logger as logging


class HerbSpecification(BaseModel):
    name: str
    confidence: float

class OptimalHerb(BaseModel):
    herb: str
    confidence: float
    herb_index: int
    region: str
    region_confidence: float
    herb_color: List[HerbSpecification] = Field(alias="color")
    herb_type: List[HerbSpecification] = Field(alias="type")

    @field_validator("herb_color")
    @classmethod
    def get_first_herb_color(cls, vehicle_spec: List[HerbSpecification]) -> str:
        return vehicle_spec[0].name

    @field_validator("herb_type")
    @classmethod
    def get_first_herb_type(cls, make_model: List[HerbSpecification]) -> str:
        return make_model[0].name.replace("_", " ")


class HarvesterConfiguration(BaseModel):
    brand: str
    min_chemical_analysis_value: Optional[float] = DEFAULT_MIN_CHEMICAL_ANALYSIS_VALUE

class HerbTechHarvest(BaseModel):
    data_type: str
    version: int
    harvest_timestamp: float = Field(alias="epoch_start")
    epoch_end: int
    company_id: str
    harvester_uid: str
    harvester_type: str
    equipment_number: str
    chemical_analysis: float
    project_uuid: Optional[str] = None
    company_uuid: str
    gps_latitude: float
    gps_longitude: float
    country: str
    crop_jpeg: Optional[str] = None
    optimal_herb: OptimalHerb
    best_confidence: float
    best_region: str
    best_region_confidence: float

    # Extra data
    harvester_configuration: HarvesterConfiguration

    @field_validator("harvest_timestamp", mode="before")
    @classmethod
    def normalize_harvest_timestamp(cls, harvest_timestamp: float) -> float:
        return harvest_timestamp / 1e3

    @computed_field
    @property
    def gps_location(self) -> str:
        return f"POINT({self.gps_longitude} {self.gps_latitude})"

    @model_validator(mode="after")
    def data_validation(self):
        chemical_analysis_must_reach_company_standards(
            self.chemical_analysis,
            self.harvester_configuration.min_chemical_analysis_value
        )
        return self

def chemical_analysis_must_reach_company_standards(chemical_analysis: float, company_standard: float):
    if chemical_analysis < company_standard:
        log_message = "Herb filtered out due to insufficient chemical analysis"
        logging.error(
            f"{log_message} | Herb chemical analysis: {chemical_analysis} | Company standard: {company_standard}"
        )
        raise ValueError("Herb filtered out due to insufficient chemical analysis")