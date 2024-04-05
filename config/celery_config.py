import os
from functools import lru_cache
from database import get_celery_url


class BaseConfig:
    broker_url: str = os.environ.get("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
    result_backend: str = f"{get_celery_url()}"
    accept_content = ['application/json']
    result_serializer = 'json'
    task_serializer = 'json'
    worker_prefetch_multiplier = 1
    broker_transport_options = {'confirm_publish': True}
    task_routes = {
        "celery_tasks.license_plate_tasks.classify_new_plate": {
            "queue": "lp.license_plate.classify"
        },
    }


class DevelopmentConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
    }
    config_name = os.environ.get("CELERY_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


celery_settings = get_settings()
