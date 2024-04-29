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
EQUIPMENT_NOT_FOUND = "Equipment not found"
UPDATE_EQUIPMENT_ERROR = "Could not update equipment"
DELETE_EQUIPMENT_ERROR = "Could not delete equipment"


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
    db_equipment = equipment_crud.get_model_instance(db=db, model_id=equipment_id, token_payload=token_payload)
    if db_equipment is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(error=EQUIPMENT_NOT_FOUND)
    return db_equipment


@router.patch("/{equipment_id}", response_model=Union[EquipmentInDB, ErrorResponse], status_code=status.HTTP_200_OK)
def update_equipment_details(
    equipment_id: int,
    equipment: EquipmentUpdate,
    response: Response,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token),
):
    if token_payload[IS_SUPERUSER] or token_payload[ROLE] in [OWNER, ADMINISTRATOR]:
        try:
            db_equipment = equipment_crud.update_model(db=db, id=equipment_id, update_schema=equipment, token_payload=token_payload)
            if db_equipment is None:
                response.status_code = status.HTTP_404_NOT_FOUND
                return ErrorResponse(error=EQUIPMENT_NOT_FOUND)
            return db_equipment
        except IntegrityError as err:
            logging.error(f"{UPDATE_EQUIPMENT_ERROR} | Error - {err.orig}")
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(error=UPDATE_EQUIPMENT_ERROR)

        except Exception as err:
            logging.error(f"{UPDATE_EQUIPMENT_ERROR} | Error - {err} \n {traceback.format_exc()}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(error=UPDATE_EQUIPMENT_ERROR)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return ErrorResponse(error=USER_FORBIDDEN)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_by_id(
    equipment_id: int,
    response: Response,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token)
):
    if token_payload[IS_SUPERUSER] or token_payload[ROLE] in [OWNER, ADMINISTRATOR]:
        try:
            success = equipment_crud.delete_model(db=db, model_id=equipment_id, token_payload=token_payload)
            if not success:
                response.status_code = status.HTTP_404_NOT_FOUND
                return ErrorResponse(error=EQUIPMENT_NOT_FOUND)
            return {"message": "Equipment deleted successfully"}
        
        except IntegrityError as err:
            logging.error(f"{DELETE_EQUIPMENT_ERROR} | Error - {err.orig}")
            response.status_code = status.HTTP_400_BAD_REQUEST
            return ErrorResponse(error=DELETE_EQUIPMENT_ERROR)

        except Exception as err:
            logging.error(f"{DELETE_EQUIPMENT_ERROR} | Error - {err} \n {traceback.format_exc()}")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return ErrorResponse(error=DELETE_EQUIPMENT_ERROR)
    else:
        response.status_code = status.HTTP_403_FORBIDDEN
        return ErrorResponse(error=USER_FORBIDDEN)
