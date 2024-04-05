from config.constants import DATA_CACHE_EXPIRATION
from config.settings import app_settings
from config.redis_keys import get_gps_key, get_camera_key
from models import Camera
from redis import Redis
from typing import Any, Awaitable, Callable, Dict, Optional, Union

Response = Union[Awaitable, Any]


class RedisService:
    def __call__(
        self,
        method_to_activate: Callable,
        *args,
        close_connection: bool = True,
        **kwargs,
    ) -> Any:
        self.redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
        self.redis.select(app_settings.REDIS_DB_INDEX)
        result = method_to_activate(self, *args, **kwargs)
        if close_connection:
            self.redis.close()
        return result

    def get_cached_agent_info(self, agent_uid: str) -> Optional[Dict[str, float]]:
        agent_cache_info = self.redis.get(get_gps_key(agent_uid), default={})
        return agent_cache_info

    def get_cached_camera(self, camera_number: str, agent_uid: str) -> Optional[Dict[str, float]]:
        return self.redis.get(get_camera_key(camera_number, agent_uid))

    def set_cached_camera(
        self,
        camera_number: str,
        agent_uid: str,
        pickled_camera: str,
        expiry_time: int = DATA_CACHE_EXPIRATION,
    ) -> Response:
        return self.redis.set(
            get_camera_key(camera_number, agent_uid), pickled_camera, ex=expiry_time
        )


def get_cached_agent_info(agent_uid: str) -> Optional[Dict[str, float]]:
    redis = Redis(host=app_settings.REDIS_HOST, port=app_settings.REDIS_PORT)
    redis.select(app_settings.REDIS_DB_INDEX)
    agent_gps_key = get_gps_key(agent_uid)
    agent_cache_info = redis.get(agent_gps_key, default={})
    redis.close()
    return agent_cache_info
