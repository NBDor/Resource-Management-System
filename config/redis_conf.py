from config.settings import app_settings
import aioredis

redis = None

async def get_redis() -> aioredis.Redis:
    redis_host = app_settings.REDIS_SERVER
    global redis
    if redis is None:
        redis = await aioredis.from_url(redis_host)
    return redis
