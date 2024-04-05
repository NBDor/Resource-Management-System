from crud.base_crud import BaseCrud
from sqlalchemy.orm import Session
from models import Equipment
from typing import Optional
from logic.redis_cache import RedisService
from log.logger import logger as logging
import pickle


class EquipmentCrud(BaseCrud):
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
