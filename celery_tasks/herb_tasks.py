from celery import shared_task
from config.settings import app_settings
from config.constants import CLASSIFY_PROCESSED_HERB
from database import get_db
from log.logger import logger as logging
from models import Herb
from shapely.wkb import loads


@shared_task(name=CLASSIFY_PROCESSED_HERB, bind=True, max_retries=3, retry_backoff=True)
def classify_processed_herb(self, herb_data: dict):
    basic_meta_data = {
        "task_name": CLASSIFY_PROCESSED_HERB,
        "UUID": herb_data['UUID'],
    }
    print(f"lp_data: {herb_data}")

    return self.request.task
