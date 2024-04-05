from config.settings import app_settings
from crud.base_crud import BaseCrud
from datetime import datetime
from models import Base, LicensePlate
from sqlalchemy import desc
from sqlalchemy.orm import Session
from log.logger import logger as logging


class LicensePlateCrud(BaseCrud):
    def get_latest_license_plate_by_plate_number(
        self, plate_number: str, live_capture_time: datetime, db: Session
    ) -> LicensePlate:
        return (
            db.query(LicensePlate)
            .filter(
                LicensePlate.plate_number == plate_number,
                LicensePlate.live_capture_time < live_capture_time,
            )
            .order_by(desc(LicensePlate.creation_time))
            .first()
        )
