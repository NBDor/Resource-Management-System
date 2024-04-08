from config.celery_utils import celery_application
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from openapi_utils.customization import custom_openapi
from routers.process_herbs import router as process_herbs_router
from routers.equipment import router as equipment_router
import uvicorn


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

base_router = APIRouter(prefix="/api/v1")
base_router.include_router(process_herbs_router)
base_router.include_router(equipment_router)
app.include_router(base_router)


app.title = "Resource Management System Fast API Backend (1.2.0)"
app.openapi = lambda: custom_openapi(app)
app.timeout_keep_alive = 30  # seconds


@app.get("/api/v1/")
async def root():
    return {"message": "Resource Management System Fast API"}


# for debugging
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
