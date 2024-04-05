from integrations.mgmt_actions import extract_agent_name
from api.models import NxCamerasMap, LicensePlate, NxServer, PlateAlert
from lp_backend.settings.constants import LOG_CONSOLE
from integrations.nx.tasks import send_plate_to_nx, send_alert_to_nx
from integrations.nx.encryption import decode_password_payload
from typing import Union

import logging

logger = logging.getLogger(LOG_CONSOLE)


# TODO: Shani's Code! - Need to refactor this...
class NxServerAPI:
    @classmethod
    def send_update_to_endpoint(
        cls, plate_information: Union[LicensePlate, PlateAlert], epoch_start=None
    ) -> None:
        # check if there is a NX model associated with the agent
        nx_instance = None
        try:
            nx_instance = NxServer.objects.get(agent_uid=plate_information.agent_uid)
            decrypted_password = decode_password_payload(nx_instance.password)[
                "password"
            ]
        except NxServer.DoesNotExist as err:
            logger.warning(
                f"[FAILED GET NxServer INSTANCE] Agent UID: {str(plate_information.agent_uid)} | NxServer.DoesNotExist exception | Error: {err}",
            )

        if nx_instance:
            nx_camera_id = None
            try:
                nx_camera_id = NxCamerasMap.objects.get(
                    camera_id=plate_information.camera.id
                ).nx_camera_id
            except NxCamerasMap.DoesNotExist as err:
                logger.warning(
                    f"[FAILED GET NxCamerasMap INSTANCE] Camera ID: {str(plate_information.camera.id)} | NxCamerasMap.DoesNotExist exception | Error: {err}",
                )

            if nx_camera_id:
                # check if the new event to send is plate event or alert event
                if type(plate_information) is LicensePlate:
                    send_plate_to_nx.delay(
                        nx_instance.username,
                        decrypted_password,
                        nx_instance.system_id,
                        plate_information.plate_number,
                        plate_information.region,
                        plate_information.agent_uid,
                        epoch_start,
                        nx_camera_id,
                        plate_information.UUID,
                        plate_information.vehicle_make_model,
                        plate_information.vehicle_color,
                        plate_information.id,
                    )
                else:
                    send_alert_to_nx.delay(
                        nx_instance.username,
                        decrypted_password,
                        nx_instance.system_id,
                        plate_information.plate_number,
                        plate_information.alert_color.color,
                        extract_agent_name(plate_information.agent_uid),
                        plate_information.camera_name,
                        plate_information.agents_group_name,
                        plate_information.agent_uid,
                        nx_camera_id,
                        plate_information.license_plate.live_capture_time,
                        plate_information.license_plate.UUID,
                        plate_information.license_plate.vehicle_make_model,
                        plate_information.license_plate.vehicle_color,
                        plate_information.license_plate.id,
                    )
