from crud.base_crud import BaseCrud
from sqlalchemy.orm import Session
from models import Camera
from typing import Optional
from logic.redis_cache import RedisService
from log.logger import logger as logging
import pickle


class CameraCrud(BaseCrud):
    async def get_camera_by_number_and_agent(
        self,
        db: Session,
        camera_number: str,
        agent_uid: str,
        token: dict,
    ) -> Optional[Camera]:
        self.base_query = await self.get_base_query_factory(db, Camera, token)
        self.redis = RedisService()
        cached_camera = self.redis(
            RedisService.get_cached_camera, camera_number, agent_uid, close_connection=False
        )
        if cached_camera:
            camera = pickle.loads(cached_camera)
        else:
            camera = self.base_query.filter(
                Camera.camera_number == camera_number,
                Camera.agent_uid == agent_uid,
            ).first()
            self.redis(
                RedisService.set_cached_camera, camera_number, agent_uid, pickle.dumps(camera)
            )
        if camera is None:
            log_message = "Camera not found in DB"
            logging.info(f"{log_message} | Agent UID: {agent_uid} | Camera Number: {camera_number}")
            raise ValueError(log_message)

        return camera
