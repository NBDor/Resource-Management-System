from config.settings import app_settings
from config.constants import IS_SUPERUSER, USER_FORBIDDEN
from crud.base_crud import BaseCrud
from decorators import base_query_factory, user_harvesters_factory
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import Equipment
from typing import Optional, List
from logic.redis_cache import RedisService
from log.logger import logger as logging
import pickle


class EquipmentCrud(BaseCrud):
    @user_harvesters_factory
    def get_model_instance(
        self,
        db: Session,
        model_id: int,
        token_payload: dict = None
    ):
        db_model = db.query(Equipment).filter(Equipment.id == model_id).first()
        if db_model and not db_model.harvester_uid in self.user_harvesters and not token_payload[IS_SUPERUSER]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=USER_FORBIDDEN)
        else:
            return db_model


    @base_query_factory(Equipment)
    def get_model_list(
        self,
        db: Session,
        harvester_uids: List[str]=[],
        skip: int = 0,
        limit: int = app_settings.PAGE_SIZE,
        token_payload: dict = None,
        # query_params: dict = {}
    ):
        self.filter_query_by_harvester_uids(harvester_uids=harvester_uids)
        # self.filter_query_by_specific_filters(query_params=query_params)
        return self.base_query.order_by(Equipment.id).offset(skip).limit(limit).all()


    @base_query_factory(Equipment)
    def get_model_list_count(
            self,
            harvester_uids: List[str],
            db: Session,
            skip: int = 0,
            limit: int = app_settings.PAGE_SIZE,
            token_payload: dict = None,
            query_params: dict = {}
        ):
            self.filter_query_by_harvester_uids(harvester_uids=harvester_uids)
            self.filter_query_by_specific_filters(query_params=query_params)
            return {"equipments_count": self.base_query.count()}


    def update_model(self, db: Session, id: int, update_schema, token_payload: dict = None):
        db_instance = self.get_model_instance(db, id, token_payload=token_payload)
        if not db_instance:
            return None
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instance, key, value)
        db.commit()
        db.refresh(db_instance)
        return db_instance


    def delete_model(self, db: Session, model_id: int, token_payload: dict = None) -> bool:
        db_instance = self.get_model_instance(db, model_id, token_payload=token_payload)
        if not db_instance:
            return False
        db.delete(db_instance)
        db.commit()
        return True


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
