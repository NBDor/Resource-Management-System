from fastapi import APIRouter, HTTPException, status, Request
from log.logger import logger as logging
from datetime import datetime


router = APIRouter(
    prefix="/push-comet-hik-plates",
    tags=["push-comet-hik-plates"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

counter = 0

@router.post("/")
async def push_comet_hik_plates(
    request: Request,
):
    _datetime = datetime.now()
    try:
        global counter
        if counter < 10:
            counter += 1
            payload = await request.json()
            f = open("hikvision_valid_payloads_2.txt", "a")
            f.write(f"\nNew Valid Session #{counter}: {_datetime} \n")
            f.write(f"request.body(): {await request.body()}\n")
            f.write(f"request.__dict__: {request.__dict__}\n")
            f.write(f"payload: {payload}\n")
            f.write("----------------------------------------------------")
            f.close()

        return {"message": "ok"}

    except HTTPException as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=f"HTTPException | Error - {err.detail}",
        )

    except Exception as err:
        logging.error(f"Server exception | Error - {err}", exc_info=True)
        f = open("hikvision_errors_2.txt", "a")
        f.write(f"\nNew Session: {_datetime} \n")
        f.write(f"request.body(): {await request.body()}\n")
        f.write(f"request.__dict__: {request.__dict__}\n")
        f.write(f"Server exception | Error - {err}")
        f.write("----------------------------------------------------")
        f.close()

        # logging.warning(f"request.body(): {await request.body()}")
        # logging.warning(f"request.__dict__: {request.__dict__}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server exception | Error - {err}",
        )
