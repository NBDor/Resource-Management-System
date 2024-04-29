from config.redis_keys import (
    get_users_queries_key,
    get_harvester_config_key,
    get_harvester_matching_details_key,
)
from config.settings import app_settings
from fastapi import HTTPException, status
from models import Base
from sqlalchemy.orm import Session
from typing import Optional, Union
from redis import Redis
import requests
import pickle
from log.logger import logger as logging



async def get_query_by_user_harvesters(
    user_uid: str, base_query: Session.query, db_model: Base
) -> Session.query:
    harvester_uids = get_user_harvesters_by_user_uid(user_uid)
    return base_query.filter(db_model.harvester_uid.in_(harvester_uids))


def get_user_harvesters_by_user_uid(user_uid: str) -> list:
    if app_settings.TESTING:
        return ["test_harvester_uid"]

    user_queries_dict = get_users_query_dict(user_uid)
    return user_queries_dict["user_harvesters"]


def get_users_query_dict(user_uid) -> dict:
    user_key = f":1:{get_users_queries_key(user_uid)}"
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cache_dict = redis.get(user_key)
    redis.close()

    user_queries_dict = (
        pickle.loads(cache_dict)
        if cache_dict
        else get_dict_from_manage_service(user_uid, "user-queries-dict")
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
        else get_info_from_manage_service_by_harvester_uid(harvester_uid, "harvester-related-info")
    )

    return device_matching_settings


async def get_harvester_configurations(harvester_uid: str) -> Union[dict, None]:
    harvester_config_key = get_harvester_config_key(harvester_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cached_configuration = redis.get(harvester_config_key)
    redis.close()

    harvester_config = (
        cached_configuration
        if cached_configuration is not None
        else get_info_from_manage_service_by_harvester_uid(harvester_uid, "harvester-configuration")
    )
    return harvester_config


def get_dict_from_manage_service(user_uid: str, manage_action: str) -> Optional[dict]:
    url = f"http://{app_settings.MANAGE_SERVICE_HOST}:{app_settings.MANAGE_SERVICE_PORT}/api/v1/{manage_action}/{user_uid}"
    send_request_to_manage_service(url, f"Failed to get user | User UID: {user_uid}")

def get_info_from_manage_service_by_harvester_uid(harvester_uid: str, manage_action: str) -> Optional[dict]:
    if app_settings.TESTING:
        return {"harvester_configurations": {"brand": "Test Brand"}}
    url = f"http://{app_settings.MANAGE_SERVICE_HOST}:{app_settings.MANAGE_SERVICE_PORT}/api/v1/{manage_action}/{harvester_uid}"
    send_request_to_manage_service(url, f"Failed to get harvester | harvester UID: {harvester_uid}")

def get_info_from_manage_service_by_project_id(project_id: str, manage_action: str) -> Optional[dict]:
    url = f"http://{app_settings.MANAGE_SERVICE_HOST}:{app_settings.MANAGE_SERVICE_PORT}/api/v1/{manage_action}/{project_id}"
    return send_request_to_manage_service(url, f"Failed to get project | Project ID: {project_id}")

def send_request_to_manage_service(url: str, error_message: str) -> Optional[str]:
    response = requests.get(url=url)
    if response.status_code != status.HTTP_200_OK:
        logging.error(
            f"[MANAGE REQUEST] {error_message} | Response: {response.status_code}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_message
        )
    else:
        return response.json()
