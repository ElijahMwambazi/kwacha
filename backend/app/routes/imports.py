from fastapi import APIRouter

router = APIRouter(prefix="/imports", tags=["imports"])


@router.get("")
def list_imports():
    return {"message": "imports endpoint scaffold"}
