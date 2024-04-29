from pydantic import BaseModel, UUID4, ConfigDict
from typing import List

class EquipmentBase(BaseModel):
    number: str
    name: str
    harvester_uid: str

class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    pass


class EquipmentInDB(EquipmentBase):
    id: int
    project_uuid: UUID4
    company_uuid: UUID4

    model_config = ConfigDict(from_attributes=True)

class EquipmentOut(EquipmentBase):
    id: int

class EquipmentsList(BaseModel):
    count: int
    results: List[EquipmentOut]

