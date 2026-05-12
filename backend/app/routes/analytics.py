from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select

from app.database import get_session
from app.models.basket import BasketItem
from app.models.item import Item
from app.models.price_observation import PriceObservation

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(
    session: Session = Depends(get_session),
):
    item_count = session.exec(select(func.count()).select_from(Item)).one()
    price_count = session.exec(select(func.count()).select_from(PriceObservation)).one()
    basket_count = session.exec(select(func.count()).select_from(BasketItem)).one()

    latest_price = session.exec(
        select(PriceObservation).order_by(
            PriceObservation.observed_at.desc(),
            PriceObservation.id.desc(),
        )
    ).first()

    return {
        "item_count": item_count,
        "price_observation_count": price_count,
        "basket_item_count": basket_count,
        "latest_price_observation": latest_price,
    }