from logic.dataclasses import HerbTechHarvest
from sqlalchemy.orm import Session
from crud.herb_crud import HerbCrud
from crud.equipment_crud import EquipmentCrud
from models import Herb, Equipment
from schemas.herb_schema import HerbCreate, HerbInDB
from schemas.equipment_schema import EquipmentInDB
from celery_tasks.herb_tasks import classify_processed_herb


class HerbTechProcessor:
    def __init__(self, incoming_harvest: HerbTechHarvest, db: Session, token_payload: dict) -> None:
        self.herb_harvest = incoming_harvest
        self.db = db
        self.herb_crud = HerbCrud(Herb)
        self.equipment_crud = EquipmentCrud(Equipment)
        self.token = token_payload

    async def process_herb_harvest(self) -> None:
        """
        This method is responsible for processing the incoming herb harvest.
        """
        herb_data = await self.gather_herb_data()

        herb_schema = HerbCreate(**herb_data)

        db_herb = self.herb_crud.create_model(
            db=self.db, create_schema=herb_schema
        )

        print(f"db_herb: {db_herb}")

        # herb_data = self.get_herb_data_for_classification(herb_in_db)

        # classify_processed_herb.delay(
        #     # herb_data=herb_data
        #     lp_data={"UUID": 2, "new_herb_id": 1}
        # )

    async def gather_herb_data(self) -> dict:
        db_equipment = await self.get_related_equipment()
        db_equipment_dict = {"equipment": EquipmentInDB(**db_equipment.__dict__)}
        herb_details = self.herb_harvest.OptimalHerb.model_dump(
            include={
                "herb_type",
                "herb_color",
                "region",
            }
        )

        herb_data = {
            **self.herb_harvest.model_dump(),
            **herb_details,
            **db_equipment_dict,
        }
        return herb_data

    async def get_related_equipment(self) -> Equipment:
        equipment = await self.equipment_crud.get_equipment_by_number_and_harvester(
            self.db, self.herb_harvest.equipment_number, self.herb_harvest.harvester_uid, token=self.token
        )
        return equipment

    def get_herb_for_classification(self, herb_in_db: HerbInDB) -> dict:
        return {
            "UUID": herb_in_db.UUID,
            "new_herb_id": herb_in_db.id,
        }
