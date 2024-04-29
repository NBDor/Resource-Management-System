from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from logic.event_processor import EventProcessor
from sqlalchemy.orm import Session
from log.logger import logger as logging


router = APIRouter(
    prefix="/process-herbs",
    tags=["Process Herbs"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def process_herbs(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        return await EventProcessor().process_request(request=request, db=db)

    except ValueError as err:
        error_message = f"ValueError | Error - {err}"
        logging.error(error_message)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": error_message}

    except HTTPException as err:
        error_message = f"HTTPException | Error - {err.detail}"
        response.status_code = err.status_code
        return {"error": error_message}

    except Exception as err:
        logging.error(f"Server exception | Error - {err}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Server exception"}
