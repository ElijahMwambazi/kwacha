from fastapi import APIRouter

router = APIRouter(prefix="/indicators", tags=["indicators"])


@router.get("")
def list_indicators():
    return {"message": "indicators endpoint scaffold"}
