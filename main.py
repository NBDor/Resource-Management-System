from config.app_operation import init_sentry
from config.celery_utils import celery_application
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from openapi_utils.customization import custom_openapi
from routers.camera import router as camera_router
from routers.license_plate import router as license_plate_router
from routers.push_plates import router as push_plates_router
from routers.push_comet_hik_plates import router as push_comet_hik_plates_router
from routers.sockets_updates import socket_app
import uvicorn

# TODO: uncomment this when sentry is ready
# init_sentry()

app = FastAPI()
app.celery_app = celery_application
celery = app.celery_app


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: change to api/v2? add a constant for the api version
base_router = APIRouter(prefix="/api/v1")
base_router.include_router(camera_router)
base_router.include_router(license_plate_router)
base_router.include_router(push_plates_router)
base_router.include_router(push_comet_hik_plates_router)
app.include_router(base_router)
app.mount("/ws/", socket_app)


app.title = "Polaris LP Fast API Backend (1.2.0)"
app.openapi = lambda: custom_openapi(app)
app.timeout_keep_alive = 30  # seconds


# TODO: change to api/v2? add a constant for the api version
@app.get("/api/v1/")
async def root():
    return {"message": "Polaris LP Fast API"}


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
