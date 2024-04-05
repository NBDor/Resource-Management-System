from database import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Any, Protocol


class HerbClassifier(Protocol):
    def __init__(self, incoming_processed_herb: Any, db: Session = Depends(get_db)) -> None:
        ...

    def classify_herb(self) -> None:
        ...
