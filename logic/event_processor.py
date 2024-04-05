from fastapi import Request
from config.constants import (
    REKOR_PLATE_RECOGNITION,
    REKOR_HEARTBEAT,
    DATA_TYPE,
    AGENT_UID,
)
from integrations.mgmt_actions import (
    get_agent_configuration,
    get_agent_details_by_agent_uid,
)
from logic.rekor_dataclasses import RekorALPR
from logic.license_plate_recognition.lp_recognizer import LicensePlateRecognizer
from logic.license_plate_recognition.rekor_recognizer import RekorRecognizer
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, Tuple


class EventProcessor:
    def __init__(self):
        self.data_type: Optional[str] = None
        self.agent_uid: Optional[str] = None
        self.event_obj: Any = None

    async def process_request(
        self,
        request: Request,
        db: Session,
        token_payload: dict,
    ) -> dict:
        payload = await request.json()
        self.data_type = payload.get(DATA_TYPE)
        self.agent_uid = payload.get(AGENT_UID)
        self.check_essential_request_data()

        if self.data_type == REKOR_PLATE_RECOGNITION:
            agent_info_dict = await self.get_agent_data()
            self.event_obj = RekorALPR(**{**payload, **agent_info_dict})
            await self.process_license_plate(RekorRecognizer(self.event_obj, db, token_payload))

        elif self.data_type == REKOR_HEARTBEAT:
            pass

        else:
            pass

        return {"message": f"Polaris system | {self.data_type.upper()} was accepted successfully"}

    def check_essential_request_data(self) -> None:
        if self.data_type is None:
            raise ValueError("Request was sent with no data_type")

        if self.agent_uid is None:
            raise ValueError("Request was sent with no agent_uid")

    async def get_agent_data(self) -> Dict[str, Any]:
        # TODO: combine all the cache/mgmt requests to one endpoint that will provide all the data (MGMT support needed)
        agent_configuration = await get_agent_configuration(self.agent_uid)
        agent_info_dict = get_agent_details_by_agent_uid(self.agent_uid)

        return {**agent_configuration, **agent_info_dict}

    async def process_license_plate(self, recognizer: LicensePlateRecognizer) -> dict:
        await recognizer.recognize_license_plate()
