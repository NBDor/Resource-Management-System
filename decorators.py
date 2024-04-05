import functools
import logging
import time
from models import Base
from integrations.mgmt_actions import (
    get_query_by_user_harvesters,
    get_user_harvesters_by_user_uid,
)
from config.constants import IS_SUPERUSER, USER_UID


def base_query_factory(db_model: Base) -> None:
    """
    This decorator is used to create & filter the db_model base_query by the user's token.
    The base_query is created according to the token's user_role.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(self, *args, **kwargs):
            token = kwargs["token"]
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
        token = kwargs.get("token", None)
        if not token:
            token = args[2]

        self.user_harvesters = []
        if not token[IS_SUPERUSER]:
            self.user_harvesters = get_user_harvesters_by_user_uid(token[USER_UID])
        value = func(self, *args, **kwargs)

        return value

    return wrapper_decorator


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
