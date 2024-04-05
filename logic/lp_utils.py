import io, base64
from logic.rekor_dataclasses import Coordinate
from models import LicensePlate
from PIL import Image
from PIL.Image import Image as PILImage
from typing import Dict, Optional
from datetime import datetime, timezone


def extract_images(
    license_plate_uuid: str,
    lq_vehicle_img=None,
    lq_plate_img=None,
    hq_vehicle_img=None,
    hq_plate_img=None,
) -> Dict[str, Optional[PILImage]]:
    lq_vehicle_img = decode_jpeg_image(
        lq_vehicle_img,
        f"lq-vehicle-{license_plate_uuid}",
    )
    lq_plate_img = decode_jpeg_image(
        lq_plate_img,
        f"lq-plate-{license_plate_uuid}",
    )
    return {
        "lq_vehicle_img": lq_vehicle_img,
        "lq_plate_img": lq_plate_img,
        "hq_vehicle_img": hq_vehicle_img,
        "hq_plate_img": hq_plate_img,
    }


def decode_jpeg_image(base64_str, file_name) -> PILImage:
    img = Image.open(io.BytesIO(base64.decodebytes(bytes(base64_str, "utf-8"))))
    img.save(f"{file_name}.jpeg")
    return img


def get_agent_latest_location(
    previous_plate: LicensePlate, agent_cache_info: Optional[Dict[str, float]]
) -> Optional[Coordinate]:
    # TODO: check if this is the optimal way to get the latest plate location
    agent_last_time = agent_cache_info.get("time", None)
    lat = agent_cache_info.get("lat", None)
    lng = agent_cache_info.get("lng", None)

    if previous_plate is None:
        if agent_last_time is None:
            return None
        else:
            return Coordinate(lat, lng)
    elif agent_last_time is None:
        return previous_plate.gps_location
    else:
        previous_plate_creation_time = previous_plate.creation_time
        if previous_plate_creation_time < agent_last_time:
            return previous_plate.gps_location
        elif previous_plate_creation_time > agent_last_time:
            return Coordinate(lat, lng)
        else:
            return None


def convert_timestamp_to_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
