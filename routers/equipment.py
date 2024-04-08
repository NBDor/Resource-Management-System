from config.settings import app_settings
from config.constants import (
    IS_SUPERUSER,
    OWNER,
    ADMINISTRATOR,
    ROLE,
    USER_FORBIDDEN,
    COMMON_DESCRIPTION,
)
from typing import Dict, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from schemas.equipment_schema import EquipmentCreate, EquipmentUpdate, EquipmentInDB
from crud.equipment_crud import EquipmentCrud
from models import Equipment
from auth.authentication import decode_access_token

from log.logger import logger as logging


equipment_crud = EquipmentCrud(Equipment)
router = APIRouter(
    prefix="/equipments",
    tags=["equipments"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)
EQUIPMENT_NOT_FOUND = "Equipment not found"

@router.post("/", response_model=EquipmentInDB, status_code=status.HTTP_201_CREATED)
def create_new_equipment(
    equipment: EquipmentCreate,
    db: Session = Depends(get_db),
    token_payload = Depends(decode_access_token)
):
    try:
        if token_payload[IS_SUPERUSER] or token_payload[ROLE] in [OWNER, ADMINISTRATOR]:
            return equipment_crud.create_model(db=db, create_schema=equipment)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=USER_FORBIDDEN)

    except IntegrityError as err:
        err_message = "Could not create equipment"
        logging.error(f"{err_message} | Error - {err.orig}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_message)

    except Exception as err:
        err_message = "Could not create equipment"
        logging.error(f"{err_message} | Error - {err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err_message)


@router.get("/count", response_model=Dict[str, int], description=COMMON_DESCRIPTION)
def get_equipments_count(
    request: Request,
    harvester_uids: List[str] = Query(default=[]),
    limit: int = 5,
    skip: int = 0,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token),
    # _: EquipmentQueryParams = Depends()
):
    return equipment_crud.get_model_list_count(
        harvester_uids=harvester_uids,
        db=db,
        skip=skip,
        limit=limit,
        token_payload=token_payload,
        query_params=dict(request.query_params)
        )


@router.get("/", response_model=List[EquipmentInDB], description=COMMON_DESCRIPTION)
def get_equipments(
    request: Request,
    harvester_uids: List[str] = Query(default=[]),
    limit: int = 5,
    skip: int = 0,
    db: Session = Depends(get_db),
    token_payload = Depends(decode_access_token),
    # query_params: EquipmentQueryParams = Depends()
):    
    results = equipment_crud.get_model_list(
        db=db,
        harvester_uids=harvester_uids,
        skip=skip,
        limit=limit,
        token_payload=token_payload,
        # query_params=dict(request.query_params)
    )
    print(f"results: {results[0].as_dict() if results else []}")
    return results


@router.get("/{equipment_id}", response_model=EquipmentInDB)
def get_equipment(
    equipment_id: int, db: Session = Depends(get_db), token_payload=Depends(decode_access_token)
):
    db_equipment = equipment_crud.get_model_instance(db=db, model_id=equipment_id, token_payload=token_payload)
    if db_equipment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EQUIPMENT_NOT_FOUND)
    return db_equipment


@router.patch("/{equipment_id}", response_model=EquipmentInDB)
def update_equipment_details(
    equipment_id: int,
    equipment: EquipmentUpdate,
    db: Session = Depends(get_db),
    token_payload=Depends(decode_access_token),
):
    if token_payload[IS_SUPERUSER] or token_payload[ROLE] in [OWNER, ADMINISTRATOR]:
        db_equipment = equipment_crud.update_model(db=db, id=equipment_id, update_schema=equipment, token_payload=token_payload)
        if db_equipment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EQUIPMENT_NOT_FOUND)
        return db_equipment
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=USER_FORBIDDEN)


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_by_id(
    equipment_id: int, db: Session = Depends(get_db), token_payload=Depends(decode_access_token)
):
    if token_payload[IS_SUPERUSER] or token_payload[ROLE] in [OWNER, ADMINISTRATOR]:
        success = equipment_crud.delete_model(db=db, model_id=equipment_id, token_payload=token_payload)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=EQUIPMENT_NOT_FOUND)
        return {"message": "Equipment deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=USER_FORBIDDEN)
