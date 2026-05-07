from fastapi import APIRouter

router = APIRouter(prefix="/basket", tags=["basket"])


@router.get("")
def list_basket():
    return {"message": "basket endpoint scaffold"}
