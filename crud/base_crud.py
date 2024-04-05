from config.constants import IS_SUPERUSER, USER_UID
from config.settings import app_settings
from integrations.mgmt_actions import get_query_by_user_agents
from models import Base
from sqlalchemy.orm import Session
from typing import Optional, List


class BaseCrud:
    def __init__(self, current_model: Base) -> None:
        self.model = current_model
        self.page_size = app_settings.PAGE_SIZE

    def get_model_instance(self, db: Session, model_id: int) -> Optional[Base]:
        return db.query(self.model).filter(self.model.id == model_id).first()

    def get_model_list(
        self, db: Session, skip: int = 0, limit: int = app_settings.PAGE_SIZE
    ) -> List[Base]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create_model(self, db: Session, create_schema) -> Base:
        db_instance = self.model(**create_schema.model_dump(exclude_unset=True))
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
        return db_instance

    def update_model(self, db: Session, id: int, update_schema) -> Optional[Base]:
        db_instance = self.get_model_instance(db, id)
        if not db_instance:
            return None
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instance, key, value)
        db.commit()
        db.refresh(db_instance)
        return db_instance

    def delete_model(self, db: Session, model_id: int) -> bool:
        db_instance = self.get_model_instance(db, model_id)
        if not db_instance:
            return False
        db.delete(db_instance)
        db.commit()
        return True

    async def get_base_query_factory(self, db: Session, db_model: Base, token: dict) -> None:
        base_query = db.query(db_model)
        if not token[IS_SUPERUSER]:
            base_query = await get_query_by_user_agents(token[USER_UID], base_query, db_model)
        return base_query
