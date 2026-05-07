from fastapi import APIRouter

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("")
def list_predictions():
    return {"message": "predictions endpoint scaffold"}
