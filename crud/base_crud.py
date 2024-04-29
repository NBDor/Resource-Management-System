from config.constants import IS_SUPERUSER, USER_UID, GET, PATCH, DELETE
from config.settings import app_settings
from decorators import check_permissions, user_harvesters_factory
from integrations.mgmt_actions import get_query_by_user_harvesters
from models import Base
from permissions.basic_permission import BasicCrudPermission
from sqlalchemy.orm import Session
from typing import Dict, Optional, List


class BaseCrud:
    def __init__(self, current_model: Base) -> None:
        self.model = current_model
        self.page_size = app_settings.PAGE_SIZE

    def create_model(self, db: Session, create_schema) -> Base:
        db_instance = self.model(**create_schema.model_dump(exclude_unset=True))
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
        return db_instance

    @user_harvesters_factory
    @check_permissions(BasicCrudPermission, method=GET)
    def get_model_instance(
            self,
            db: Session,
            model_id: int,
            token_payload: dict = None
    ) -> Optional[Base]:
        return db.query(self.model).filter(self.model.id == model_id).first()

    def get_model_list(
            self,
            skip: int = 0,
            limit: int = app_settings.PAGE_SIZE
    ) -> Dict[int, List[Base]]:
        return {
            "count": self.base_query.count(),
            "results": self.base_query.order_by(self.model.id).offset(skip).limit(limit).all()
        }

    @user_harvesters_factory
    @check_permissions(BasicCrudPermission, method=PATCH)
    def update_model(
        self,
        db: Session,
        model_id: int,
        update_schema,
        token_payload: dict = None,
    ) -> Optional[Base]:
        db_instance = self.get_model_instance(db, model_id, token_payload)
        if not db_instance:
            return None
        update_data = update_schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_instance, key, value)
        db.commit()
        db.refresh(db_instance)
        return db_instance

    @user_harvesters_factory
    @check_permissions(BasicCrudPermission, method=DELETE)
    def delete_model(self, db: Session, model_id: int, token_payload: dict = None) -> bool:
        db_instance = self.get_model_instance(db, model_id, token_payload)
        if db_instance:
            db.delete(db_instance)
            db.commit()
            return True
        return False

    async def get_base_query_factory(self, db: Session, db_model: Base, token: dict) -> None:
        base_query = db.query(db_model)
        if not token[IS_SUPERUSER]:
            base_query = await get_query_by_user_harvesters(token[USER_UID], base_query, db_model)
        return base_query
