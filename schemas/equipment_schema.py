from pydantic import BaseModel, UUID4, ConfigDict
from typing import Optional, List

class EquipmentBase(BaseModel):
    number: str
    name: str
    harvester_uid: str

class EquipmentCreate(EquipmentBase):
    project_uuid: UUID4
    company_uuid: UUID4


class EquipmentUpdate(EquipmentBase):
    number: Optional[str] = None
    name: Optional[str] = None
    harvester_uid: Optional[str] = None
    project_uuid: Optional[UUID4] = None
    company_uuid: Optional[UUID4] = None


class EquipmentInDB(EquipmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class EquipmentOut(EquipmentBase):
    id: int

class EquipmentsList(BaseModel):
    count: int
    results: List[EquipmentOut]

