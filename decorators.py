from config.constants import IS_SUPERUSER, USER_UID, USER_FORBIDDEN, ROLE
from fastapi import HTTPException, status, Request
import functools
from schemas.general_schema import ErrorResponse
from integrations.mgmt_actions import (
    get_query_by_user_harvesters,
    get_user_harvesters_by_user_uid,
)
import logging
from models import Base
import time
import traceback
from permissions.basic_permission import BasicPermission
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import TypeVar, Type

T = TypeVar('T', bound='BasicPermission')

def exception_handler(custom_error_message: str=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            try:
                response = kwargs["response"]
                return func(*args, **kwargs)
            
            except IntegrityError as err:
                logging.error(f"{custom_error_message} | Error - {err.orig} \n {traceback.format_exc()}")
                response.status_code = status.HTTP_400_BAD_REQUEST
                error = custom_error_message

            except PermissionError as err:
                logging.error(f"{custom_error_message} | Error - {err} \n {traceback.format_exc()}")
                response.status_code = status.HTTP_403_FORBIDDEN
                error = USER_FORBIDDEN
            
            except HTTPException as err:
                response.status_code = status.HTTP_404_NOT_FOUND
                error = err.detail

            except Exception as err:
                logging.error(f"{custom_error_message} | Error - {err} \n {traceback.format_exc()}")
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                error = custom_error_message
            
            return ErrorResponse(error=error)

        return wrapper_decorator
    
    return decorator

def base_query_factory(db_model: Base) -> None:
    """
    This decorator is used to create & filter the db_model base_query by the user's token.
    The base_query is created according to the token's user_role.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(self, *args, **kwargs):
            token = kwargs["token_payload"]
            db = kwargs["db"]

            self.base_query = db.query(db_model)
            if not token[IS_SUPERUSER]:
                self.base_query = get_query_by_user_harvesters(
                    token[USER_UID], self.base_query, db_model
                )

            value = func(self, *args, **kwargs)

            return value

        return wrapper_decorator

    return decorator

def user_harvesters_factory(func):
    @functools.wraps(func)
    def wrapper_decorator(self, *args, **kwargs):
        token = kwargs.get("token_payload", None)
        if not token:
            token = args[2]

        self.user_harvesters = []
        self.is_superuser = False

        if token[IS_SUPERUSER]:
            self.is_superuser = True
        else:
            self.user_harvesters = get_user_harvesters_by_user_uid(token[USER_UID])
        value = func(self, *args, **kwargs)

        return value

    return wrapper_decorator

def check_permissions(permission_policy_class: Type[T], method: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, db: Session, model_id: str, *args, **kwargs):
            token = kwargs.get("token_payload", None)
            
            is_superuser = token[IS_SUPERUSER]
            role = token[ROLE]
            model = self.model
            model_harvester_uid = model.get_harvester_uid(model, db, model_id)
            permission_policy = permission_policy_class(
                is_superuser,
                method,
                role,
                model_harvester_uid,
                user_harvesters=self.user_harvesters
            )
            if not permission_policy.has_permission():
                raise PermissionError("User doesn't have permission to access this resource.")

            return func(self, db, model_id, *args, **kwargs)
        return wrapper
    return decorator

def calc_run_time(func):
    @functools.wraps(func)
    def wrapper_decorator(self, *args, **kwargs):
        t1 = time.time()
        value = func(self, *args, **kwargs)
        t2 = time.time() - t1
        func_name = str(func).split("function ")[1].split(" at")[0]
        logging.info(f"Function: '{func_name}' ran in {t2} seconds")

        return value

    return wrapper_decorator
