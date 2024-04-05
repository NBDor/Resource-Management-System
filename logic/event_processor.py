from fastapi import HTTPException, status, Request
from config.constants import (
    HERBTECH_HARVESTER,
    HERBTECH_HEARTBEAT,
    DATA_TYPE,
    HARVESTER_UID,
)
from integrations.mgmt_actions import (
    get_harvester_configuration,
    get_harvester_details_by_harvester_uid,
)
from log import logger
from logic.dataclasses import HerbTechHarvest
from logic.herb_processing.abstract_processor import AbstractProcessor
from logic.herb_processing.herb_tech_processor import HerbTechProcessor
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional


class EventProcessor:
    def __init__(self):
        self.data_type: Optional[str] = None
        self.harvester_uid: Optional[str] = None
        self.event_obj: Any = None

    async def process_request(
        self,
        request: Request,
        db: Session,
        token_payload: dict,
    ) -> dict:
        payload = await request.json()
        self.data_type = payload.get(DATA_TYPE)
        self.harvester_uid = payload.get(HARVESTER_UID)
        self.check_essential_request_data(self.data_type, self.harvester_uid)

        if self.data_type == HERBTECH_HARVESTER:
            harvester_info_dict = await self.get_harvester_data()
            self.event_obj = HerbTechHarvest(**{**payload, **harvester_info_dict})
            await self.process_herb(HerbTechProcessor(self.event_obj, db, token_payload))

        elif self.data_type == HERBTECH_HEARTBEAT:
            pass

        else:
            warning_message = f"Unknown data type: {self.data_type}"
            logger.warning(warning_message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=warning_message,
            )

        return {"message": f"RMS system | {self.data_type.upper()} was accepted successfully"}

    def check_essential_request_data(**kwargs) -> None:
        for key, value in kwargs.items():
            if value is None:
                raise ValueError(f"Request was sent with no {key}")

    async def get_harvester_data(self) -> Dict[str, Any]:
        harvester_configuration = await get_harvester_configuration(self.harvester_uid)
        harvester_info_dict = get_harvester_details_by_harvester_uid(self.harvester_uid)
        return {**harvester_configuration, **harvester_info_dict}

    async def process_herb(self, herb_processor: AbstractProcessor) -> dict:
        await herb_processor.process_herb_harvest()
