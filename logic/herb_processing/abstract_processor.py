from database import get_db
from fastapi import Depends
from models import Equipment
from sqlalchemy.orm import Session
from typing import Any, Protocol


class AbstractProcessor(Protocol):
    def __init__(self, incoming_rekor_lpr: Any, db: Session = Depends(get_db)) -> None:
        ...

    def process_herb_harvest(self) -> None:
        ...

    def get_related_equipment(self) -> Equipment:
        ...

    def extract_lp_info(self):
        ...

    def calc_direction_of_travel_degrees(self) -> float:
        ...
