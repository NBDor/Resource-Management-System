from celery.result import AsyncResult
from celery import Celery
from .celery_config import celery_settings


def create_celery():
    celery_app = Celery('RMS')
    celery_app.config_from_object(celery_settings, namespace='CELERY')
    celery_app.conf.update(task_track_started=True)
    celery_app.conf.update(task_serializer='json')
    celery_app.conf.update(result_serializer='json')
    celery_app.conf.update(result_expires=0)
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(worker_send_task_events=True)
    celery_app.conf.update(broker_connection_retry_on_startup=True)
    celery_app.conf.update(task_reject_on_worker_lost=True)
    celery_app.conf.update(task_acks_late=True)
    # celery_app.conf.update(broker_heartbeat=None)
    celery_app.conf.update(worker_cancel_long_running_tasks_on_connection_loss=True)

    return celery_app

celery_application = create_celery()



def get_task_info(task_id):
    """
    return task info for the given task_id
    """
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return result
