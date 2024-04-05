from config.redis_keys import (
    get_users_queries_key,
    get_harvester_config_key,
    get_harvester_matching_details_key,
)
from config.settings import app_settings
from models import Base
from sqlalchemy.orm import Session
from typing import Optional, Union
from redis import Redis
import requests
import pickle
from log.logger import logger as logging


async def get_user_harvesters_by_user_uid(user_uid: str) -> list:
    user_queries_dict = await get_users_query_dict(user_uid)
    return user_queries_dict["user_harvesters"]


async def get_query_by_user_harvesters(
    user_uid: str, base_query: Session.query, db_model: Base
) -> Session.query:
    harvester_uids = await get_user_harvesters_by_user_uid(user_uid)
    return base_query.filter(db_model.harvester_uid.in_(harvester_uids))


async def get_users_query_dict(user_uid) -> dict:
    user_key = f":1:{get_users_queries_key(user_uid)}"
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cache_dict = redis.get(user_key)
    redis.close()

    user_queries_dict = (
        pickle.loads(cache_dict)
        if cache_dict
        else await get_dict_from_mgmt(user_uid, "user-queries-dict")
    )

    return user_queries_dict


def get_harvester_details_by_harvester_uid(harvester_uid: str) -> str:
    harvester_key = get_harvester_matching_details_key(harvester_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cache_dict = redis.get(harvester_key)
    redis.close()

    device_matching_settings = (
        cache_dict
        if cache_dict
        else get_info_from_mgmt_by_harvester_uid(harvester_uid, "harvester-related-info")
    )

    return device_matching_settings


async def get_harvester_configuration(harvester_uid: str) -> Union[dict, None]:
    harvester_config_key = get_harvester_config_key(harvester_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cached_configuration = redis.get(harvester_config_key)
    redis.close()

    harvester_config = (
        cached_configuration
        if cached_configuration is not None
        else get_info_from_mgmt_by_harvester_uid(harvester_uid, "harvester-configuration")
    )
    return harvester_config


async def get_dict_from_mgmt(user_uid: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related harvester's information.
    """
    url = f"http://{app_settings.MGMT_SERVICE_HOST}:{app_settings.MGMT_SERVICE_PORT}/api/v1/{mgmt_action}/{user_uid}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logging.error(
            f"[MGMT REQUEST] Failed to get user | User UID: {user_uid} | Response: {response.status_code}"
        )
        raise Exception(f"Failed to get user | User UID: {user_uid}")
    else:
        return response.json()


def get_info_from_mgmt_by_harvester_uid(harvester_uid: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related harvester's information.
    """
    url = f"http://{app_settings.MGMT_SERVICE_HOST}:{app_settings.MGMT_SERVICE_PORT}/api/v1/{mgmt_action}/{harvester_uid}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logging.error(
            f"[MGMT REQUEST] Failed to get harvester | harvester UID: {harvester_uid} | Response: {response.status_code}"
        )
        raise Exception(f"Failed to get harvester | harvester UID: {harvester_uid}")
    else:
        return response.json()


def get_info_from_mgmt_by_project_id(project_id: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related project's information.
    """
    url = f"http://{app_settings.MGMT_SERVICE_HOST}:{app_settings.MGMT_SERVICE_PORT}/api/v1/{mgmt_action}/{project_id}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logging.error(
            f"[MGMT REQUEST] Failed to get project | Project ID: {project_id} | Response: {response.status_code}"
        )
        raise Exception(f"Failed to get project | Project ID: {project_id}")
    else:
        return response.json()
