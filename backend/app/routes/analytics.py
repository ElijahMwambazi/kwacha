from typing import Any

from fastapi import APIRouter, Depends, Query
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


@router.get("/price-trends")
def get_price_trends(
    item_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    statement = (
        select(PriceObservation, Item)
        .join(Item, PriceObservation.item_id == Item.id)
        .order_by(PriceObservation.observed_at.asc(), PriceObservation.id.asc())
    )

    if item_id is not None:
        statement = statement.where(PriceObservation.item_id == item_id)

    rows = session.exec(statement).all()

    return [
        {
            "price_id": observation.id,
            "item_id": item.id,
            "item_name": item.name,
            "shop_name": observation.shop_name,
            "location": observation.location,
            "price": observation.price,
            "quantity": observation.quantity,
            "unit": observation.unit,
            "price_per_unit": observation.price_per_unit,
            "observed_at": observation.observed_at,
        }
        for observation, item in rows
    ]


@router.get("/shop-comparison")
def get_shop_comparison(
    item_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
) -> list[dict[str, Any]]:
    statement = (
        select(
            PriceObservation.item_id,
            Item.name,
            PriceObservation.shop_name,
            PriceObservation.location,
            func.count(PriceObservation.id),
            func.min(PriceObservation.price_per_unit),
            func.max(PriceObservation.price_per_unit),
            func.avg(PriceObservation.price_per_unit),
        )
        .join(Item, PriceObservation.item_id == Item.id)
        .group_by(
            PriceObservation.item_id,
            Item.name,
            PriceObservation.shop_name,
            PriceObservation.location,
        )
        .order_by(Item.name.asc(), func.avg(PriceObservation.price_per_unit).asc())
    )

    if item_id is not None:
        statement = statement.where(PriceObservation.item_id == item_id)

    rows = session.exec(statement).all()

    return [
        {
            "item_id": item_id_value,
            "item_name": item_name,
            "shop_name": shop_name,
            "location": location,
            "observation_count": observation_count,
            "min_price_per_unit": round(min_price_per_unit, 2),
            "max_price_per_unit": round(max_price_per_unit, 2),
            "avg_price_per_unit": round(avg_price_per_unit, 2),
        }
        for (
            item_id_value,
            item_name,
            shop_name,
            location,
            observation_count,
            min_price_per_unit,
            max_price_per_unit,
            avg_price_per_unit,
        ) in rows
    ]