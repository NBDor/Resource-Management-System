from auth.authentication import decode_access_token
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Request
from logic.event_processor import EventProcessor
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/push-plates",
    tags=["push-plates"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.post("/")
async def push_plates(
    request: Request,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(decode_access_token),
):
    return await EventProcessor().process_request(
        request=request, db=db, token_payload=token_payload
    )


# try:

# except HTTPException as err:
#     raise HTTPException(
#         status_code=err.status_code,
#         detail=f"HTTPException | Error - {err.detail}",
#     )

# except Exception as err:
#     raise HTTPException(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         detail=f"Server exception | Error - {err}",
#     )
