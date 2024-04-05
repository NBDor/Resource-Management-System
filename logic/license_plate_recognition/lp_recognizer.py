from database import get_db
from fastapi import Depends
from logic.rekor_dataclasses import Coordinate
from models import Camera, LicensePlate
from PIL.Image import Image as PILImage
from sqlalchemy.orm import Session
from typing import Any, Optional, Dict, Protocol, Tuple


class LicensePlateRecognizer(Protocol):
    def __init__(self, incoming_rekor_lpr: Any, db: Session = Depends(get_db)) -> None:
        ...

    def recognize_license_plate(self) -> None:
        ...

    def get_related_camera(self) -> Camera:
        ...

    def validate_agents_group_name(self, db_agents_group_name) -> None:
        ...

    def extract_images(self) -> Tuple[PILImage, PILImage]:
        ...

    def extract_lp_info(self):
        ...

    def calc_direction_of_travel_degrees(self) -> float:
        ...

    def get_previous_license_plate(self) -> LicensePlate:
        ...
