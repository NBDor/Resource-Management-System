from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Request
from logic.event_processor import EventProcessor
from sqlalchemy.orm import Session
from log.logger import logger as logging


router = APIRouter(
    prefix="/process-herbs",
    tags=["process-herbs"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/")
async def process_herbs(
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        return await EventProcessor().process_request(request=request, db=db)

    except ValueError as err:
        error_message = f"ValueError | Error - {err}"
        logging.error(error_message)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message,
        )

    except HTTPException as err:
        error_message = f"HTTPException | Error - {err.detail}"
        raise HTTPException(
            status_code=err.status_code,
            detail=error_message,
        )

    except Exception as err:
        logging.error(f"Server exception | Error - {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server exception",
        )
