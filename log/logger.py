from config.settings import logging_dict, app_settings
import logging

logging.basicConfig(
    level=logging_dict[app_settings.LOG_LEVEL],
    format='%(asctime)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger("rms")
