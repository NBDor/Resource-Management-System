from config.constants import (
    IS_SUPERUSER,
    OWNER,
    ADMINISTRATOR,
    ROLE,
    USER_FORBIDDEN,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from decorators import exception_handler
from fastapi import APIRouter, Depends, status, Response
from schemas.general_schema import ErrorResponse
from schemas.equipment_schema import EquipmentCreate, EquipmentUpdate, EquipmentInDB, EquipmentsList
from crud.equipment_crud import EquipmentCrud
from models import Equipment
from auth.authentication import decode_access_token
from typing import Union
import traceback

from log.logger import logger as logging


equipment_crud = EquipmentCrud(Equipment)
router = APIRouter(
    prefix="/equipments",
    tags=["Equipments"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Union[EquipmentInDB, ErrorResponse], status_code=status.HTTP_201_CREATED)
@exception_handler(custom_error_message="Could not create equipment")
def create_new_equipment(
    equipment: EquipmentCreate,
    response: Response,
    db: Session = Depends(get_db),
    token_payload = Depends(decode_access_token)
):
    return equipment_crud.create_model(db=db, create_schema=equipment)


@router.get("/", response_model=Union[EquipmentsList, ErrorResponse], status_code=status.HTTP_200_OK)
@exception_handler(custom_error_message="Could not list equipments")
def get_equipments(
    response: Response,
    limit: int = 5,
    skip: int = 0,
    db: Session = Depends(get_db),
    token_payload = Depends(decode_access_token),
):   
    return equipment_crud.get_model_list(
        db=db,
        skip=skip,
        limit=limit,
        token_payload=token_payload,
    )


@router.get("/{equipment_id}", response_model=Union[EquipmentInDB, ErrorResponse], status_code=status.HTTP_200_OK)
@exception_handler(custom_error_message="Could not get equipment")
def get_equipment(
    equipment_id: int,
    response: Response,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token)
):
    return equipment_crud.get_model_instance(db=db, model_id=equipment_id, token_payload=token_payload)


@router.patch("/{equipment_id}", response_model=Union[EquipmentInDB, ErrorResponse], status_code=status.HTTP_200_OK)
@exception_handler(custom_error_message="Could not update equipment")
def update_equipment_details(
    equipment_id: int,
    equipment: EquipmentUpdate,
    response: Response,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token),
):
    return equipment_crud.update_model(db=db, model_id=equipment_id, update_schema=equipment, token_payload=token_payload)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
@exception_handler(custom_error_message="Could not delete equipment")
def delete_equipment_by_id(
    equipment_id: int,
    response: Response,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token)
):
    return equipment_crud.delete_model(db=db, model_id=equipment_id, token_payload=token_payload)
