from fastapi import APIRouter

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("")
def list_prices():
    return {"message": "prices endpoint scaffold"}
