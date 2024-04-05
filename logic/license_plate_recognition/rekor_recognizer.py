from config.constants import COMET_PRO_BRAND, METEOR_BRAND, ENABLED
from config.settings import app_settings
from celery_tasks.license_plate_tasks import classify_new_plate
from crud.camera_crud import CameraCrud
from crud.license_plate_crud import LicensePlateCrud
from datetime import datetime, timezone

from logic.angle_calculator import calc_angle_between_two_coordinates
from logic.lp_utils import extract_images, get_agent_latest_location
from logic.redis_cache import get_cached_agent_info
from logic.rekor_dataclasses import RekorALPR, Coordinate
from schemas.license_plate_schema import LicensePlateCreate, LicensePlateInDB
from schemas.camera_schema import CameraInDB
from models import Camera, LicensePlate
from sqlalchemy.orm import Session


class RekorRecognizer:
    def __init__(self, incoming_rekor_lpr: RekorALPR, db: Session, token_payload: dict) -> None:
        self.rekor_lpr = incoming_rekor_lpr
        self.db = db
        self.license_plate_crud = LicensePlateCrud(LicensePlate)
        self.camera_crud = CameraCrud(Camera)
        self.token = token_payload

    async def recognize_license_plate(self) -> None:
        """
        This method is responsible for processing the incoming license plate recognition event.
        """
        lpr_data = await self.gather_license_plate_data()

        license_plate_schema = LicensePlateCreate(**lpr_data)

        db_license_plate = self.license_plate_crud.create_model(
            db=self.db, create_schema=license_plate_schema
        )

        print(f"db_license_plate: {db_license_plate}")

        self.external_services()

        # lp_data = self.get_lp_data_for_classification(license_plate_in_db)

        # classify_new_plate.delay(
        #     # lp_data=lp_data
        #     lp_data={"UUID": 2, "new_plate_id": 1}
        # )

    async def gather_license_plate_data(self) -> dict:
        db_camera = await self.get_related_camera()
        db_camera_dict = {"camera": CameraInDB(**db_camera.__dict__)}
        direction_of_travel_degrees = {
            "direction_of_travel_degrees": self.calc_direction_of_travel_degrees()
        }
        vehicle_details = self.rekor_lpr.vehicle.model_dump(
            include={
                "vehicle_body_type",
                "vehicle_color",
                "vehicle_make",
                "vehicle_make_model",
            }
        )
        best_plate_details = self.rekor_lpr.best_plate.model_dump(
            include={"region", "plate_crop_jpeg", "coordinates"}
        )
        lp_images = extract_images(
            license_plate_uuid=self.rekor_lpr.license_plate_uuid,
            lq_vehicle_img=self.rekor_lpr.vehicle_crop_jpeg,
            lq_plate_img=self.rekor_lpr.best_plate.plate_crop_jpeg,
        )

        lpr_data = {
            **self.rekor_lpr.model_dump(),
            **vehicle_details,
            **lp_images,
            **best_plate_details,
            **direction_of_travel_degrees,
            **db_camera_dict,
        }
        return lpr_data

    async def get_related_camera(self) -> Camera:
        camera = await self.camera_crud.get_camera_by_number_and_agent(
            self.db, self.rekor_lpr.camera_number, self.rekor_lpr.agent_uid, token=self.token
        )
        return camera

    def calc_direction_of_travel_degrees(self) -> float:
        # TODO: remove when the LP models are ready:
        return 0.0

        if self.rekor_lpr.agent_configuration.brand in [COMET_PRO_BRAND, METEOR_BRAND]:
            previous_plate = self.get_previous_license_plate()
            agent_cache_info = get_cached_agent_info(self.rekor_lpr.agent_uid)

            agent_latest_location = get_agent_latest_location(
                previous_plate=previous_plate, agent_cache_info=agent_cache_info
            )
            agent_current_location = Coordinate(
                self.rekor_lpr.gps_latitude, self.rekor_lpr.gps_longitude
            )
            return calc_angle_between_two_coordinates(
                agent_latest_location=agent_latest_location,
                agent_current_location=agent_current_location,
            )
        else:
            return -1

    def get_previous_license_plate(self) -> LicensePlate:
        return self.license_plate_crud.get_latest_license_plate_by_plate_number(
            plate_number=self.rekor_lpr.best_plate_number,
            live_capture_time=datetime.fromtimestamp(
                self.rekor_lpr.live_capture_timestamp, tz=timezone.utc
            ),
            db=self.db,
        )

    def external_services(self):
        # TODO: refactor and resolve the issues with nx_server.py and webhooks.py files
        # if app_settings.NX_INTEGRATION == ENABLED:
        #     NxServerAPI.send_update_to_endpoint(
        #         self.new_plate, self.lpr_payload_obj.epoch_start
        #     )
        pass

    def get_lp_data_for_classification(self, license_plate_in_db: LicensePlateInDB) -> dict:
        return {
            "UUID": license_plate_in_db.UUID,
            "new_plate_id": license_plate_in_db.id,
        }
