from config.redis_keys import (
    get_users_queries_key,
    get_agent_config_key,
    get_agent_matching_details_key,
    get_agent_url_key,
)
from config.settings import app_settings
from models import Base
from sqlalchemy.orm import Session
from typing import Optional, Union
from redis import Redis
import requests
import pickle
from log.logger import logger as logging


async def get_user_agents_by_user_uid(user_uid: str) -> list:
    user_queries_dict = await get_users_query_dict(user_uid)
    return user_queries_dict["user_agents"]


async def get_query_by_user_agents(
    user_uid: str, base_query: Session.query, db_model: Base
) -> Session.query:
    agent_uids = await get_user_agents_by_user_uid(user_uid)
    return base_query.filter(db_model.agent_uid.in_(agent_uids))


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


def get_agent_details_by_agent_uid(agent_uid: str) -> str:
    agent_key = get_agent_matching_details_key(agent_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cache_dict = redis.get(agent_key)
    redis.close()

    device_matching_settings = (
        cache_dict
        if cache_dict
        else get_info_from_mgmt_by_agent_uid(agent_uid, "agent-related-info")
    )

    return device_matching_settings


async def get_agent_configuration(agent_uid: str) -> Union[dict, None]:
    agent_config_key = get_agent_config_key(agent_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cached_configuration = redis.get(agent_config_key)
    redis.close()

    agent_config = (
        cached_configuration
        if cached_configuration is not None
        else get_info_from_mgmt_by_agent_uid(agent_uid, "agent-configuration")
    )
    return agent_config


async def get_agent_alert_url(agent_uid: str) -> str:
    agent_url_key = get_agent_url_key(agent_uid)
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    cached_agent_url = redis.get(agent_url_key)
    redis.close()

    agent_alert_url = (
        cached_agent_url
        if cached_agent_url is not None
        else get_info_from_mgmt_by_agent_uid(agent_uid, "agent-alerts-url")
    )
    return agent_alert_url["agent_alerts_url"]


async def get_dict_from_mgmt(user_uid: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related agent's information.
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


def get_info_from_mgmt_by_agent_uid(agent_uid: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related agent's information.
    """
    url = f"http://{app_settings.MGMT_SERVICE_HOST}:{app_settings.MGMT_SERVICE_PORT}/api/v1/{mgmt_action}/{agent_uid}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logging.error(
            f"[MGMT REQUEST] Failed to get agent | Agent UID: {agent_uid} | Response: {response.status_code}"
        )
        raise Exception(f"Failed to get agent | Agent UID: {agent_uid}")
    else:
        return response.json()


def get_info_from_mgmt_by_agents_group_id(agents_group_id: str, mgmt_action: str) -> Optional[str]:
    """
    This method asks the management service for the related agents group's information.
    """
    url = f"http://{app_settings.MGMT_SERVICE_HOST}:{app_settings.MGMT_SERVICE_PORT}/api/v1/{mgmt_action}/{agents_group_id}"
    response = requests.get(url=url)
    if response.status_code != 200:
        logging.error(
            f"[MGMT REQUEST] Failed to get agent group | Agent Group ID: {agents_group_id} | Response: {response.status_code}"
        )
        raise Exception(f"Failed to get agent group | Agent Group ID: {agents_group_id}")
    else:
        return response.json()
