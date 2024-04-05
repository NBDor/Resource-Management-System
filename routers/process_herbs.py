from auth.authentication import decode_access_token
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Request
from logic.event_processor import EventProcessor
from sqlalchemy.orm import Session
from log import logger

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
    token_payload: dict = Depends(decode_access_token),
):
    try:
        return await EventProcessor().process_request(
            request=request, db=db, token_payload=token_payload
        )

    except HTTPException as err:
        logger.error(f"HTTPException | Error - {err.detail}")
        raise HTTPException(
            status_code=err.status_code,
            detail="HTTPException",
        )

    except Exception as err:
        logger.error(f"Server exception | Error - {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server exception",
        )
