from pydantic import BaseModel


class EquipmentBase(BaseModel):
    number: str
    harvester_uid: str
    name: str
    project_uuid: str
    company_uuid: str


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(EquipmentBase):
    pass


class EquipmentInDB(EquipmentBase):
    id: int
