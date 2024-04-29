from config.settings import app_settings
from crud.base_crud import BaseCrud
from decorators import base_query_factory
from fastapi import HTTPException, status
from models import Equipment
from typing import Optional, List
from sqlalchemy.orm import Session
from logic.redis_cache import RedisService
from log.logger import logger as logging
import pickle


EQUIPMENT_NOT_FOUND = "Equipment not found"


class EquipmentCrud(BaseCrud):

    def get_model_instance(
        self,
        db: Session,
        model_id: int,
        token_payload: dict = None
    ):
        db_model = super().get_model_instance(db, model_id, token_payload=token_payload)
        if not db_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=EQUIPMENT_NOT_FOUND,
            )
        return db_model


    @base_query_factory(Equipment)
    def get_model_list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = app_settings.PAGE_SIZE,
        token_payload: dict = None,
    ):
        return super().get_model_list(skip, limit)


    def update_model(
            self,
            db: Session,
            model_id: int,
            update_schema,
            token_payload: dict = None,
    ):
        db_instance = super().update_model(
            db=db,
            model_id=model_id,
            update_schema=update_schema,
            token_payload=token_payload,
        )
        if db_instance is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=EQUIPMENT_NOT_FOUND,
            )
        return db_instance


    def delete_model(self, db: Session, model_id: int, token_payload: dict = None) -> bool:
        success = super().delete_model(
            db=db,
            model_id=model_id,
            token_payload=token_payload,
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=EQUIPMENT_NOT_FOUND,
            )
        return success


    def filter_query_by_harvester_uids(self, harvester_uids: List[str]) -> None:
        if harvester_uids and len(harvester_uids) > 0:
            self.base_query = self.base_query.filter(Equipment.harvester_uid.in_(harvester_uids))


    async def get_equipment_by_number_and_harvester(
        self,
        db: Session,
        equipment_number: str,
        harvester_uid: str,
    ) -> Optional[Equipment]:
        self.base_query = db.query(Equipment)

        self.redis = RedisService()
        cached_equipment = self.redis(
            RedisService.get_cached_equipment, equipment_number, harvester_uid, close_connection=False
        )
        if cached_equipment:
            equipment = pickle.loads(cached_equipment)
        else:
            equipment = self.base_query.filter(
                Equipment.number == equipment_number,
                Equipment.harvester_uid == harvester_uid,
            ).first()
            self.redis(
                RedisService.set_cached_equipment, equipment_number, harvester_uid, pickle.dumps(equipment)
            )
        if equipment is None:
            log_message = "Equipment not found in DB"
            logging.info(f"{log_message} | Harvester UID: {harvester_uid} | Equipment Number: {equipment_number}")
            raise ValueError(log_message)

        return equipment
