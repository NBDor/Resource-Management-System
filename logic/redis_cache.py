from config.constants import DATA_CACHE_EXPIRATION
from config.settings import app_settings
from config.redis_keys import get_equipment_key
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

    def get_cached_equipment(self, equipment_number: str, harvester_uid: str) -> Optional[Dict[str, float]]:
        return self.redis.get(get_equipment_key(equipment_number, harvester_uid))

    def set_cached_equipment(
        self,
        equipment_number: str,
        harvester_uid: str,
        pickled_equipment: str,
        expiry_time: int = DATA_CACHE_EXPIRATION,
    ) -> Response:
        return self.redis.set(
            get_equipment_key(equipment_number, harvester_uid), pickled_equipment, ex=expiry_time
        )
