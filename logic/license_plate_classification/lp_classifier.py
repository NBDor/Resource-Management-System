from database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Protocol


class LicensePlateClassifier(Protocol):
    def __init__(self, incoming_rekor_lpr: Any, db: Session = Depends(get_db)) -> None:
        ...

    def classify_license_plate(self) -> None:
        ...
