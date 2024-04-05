from celery import shared_task
from config.settings import app_settings
from config.constants import CLASSIFY_NEW_PLATE
from database import get_db
from log.logger import logger as logging

from shapely.wkb import loads


@shared_task(name=CLASSIFY_NEW_PLATE, bind=True, max_retries=3, retry_backoff=True)
def classify_new_plate(self, lp_data: dict):
    basic_meta_data = {
        "task_name": CLASSIFY_NEW_PLATE,
        "UUID": lp_data['UUID'],
    }
    print(f"lp_data: {lp_data}")
    # failed_meta_dict = {
    #     "task_name": CLASSIFY_NEW_PLATE,
    #     "license_plate_id": new_plate_id,
    #     "number_of_retries": number_of_retries,
    #     "task_first_failure_time": task_first_failure_time,
    # }
    # success_meta_dict = {
    #     "task_name": CLASSIFY_NEW_PLATE,
    #     "plate_number": new_plate.plate_number,
    #     "UUID": new_plate.UUID,
    # }

    try:
        new_plate = LicensePlate.objects.get(id=new_plate_id)
        failed_meta_dict["UUID"] = new_plate.UUID
        Classifications(new_plate).classify_plate_actions()
        if is_rekor_source(new_plate.agent_uid):
            async_validate_license_plate_creation.delay(created=True, license_plate_id=new_plate_id)
    except LicensePlate.DoesNotExist as err:
        log_message = "[CLASSIFY PLATE] Failed get license plate | License Plate ID:" + str(
            new_plate_id
        )
        error_message = str(type(err).__name__) + "(" + str(err) + ")"
        handle_failed_task_data(self, failed_meta_dict, log_message, error_message, ERROR)
    except Exception as err:
        error_message = str(type(err).__name__) + "(" + str(err) + ")"
        log_message = f"[CLASSIFY PLATE] Exception error: {error_message}"
        handle_failed_task_data(self, failed_meta_dict, log_message, error_message, ERROR)

    # return json.loads(json.dumps(success_meta_dict))
    return self.request.task
