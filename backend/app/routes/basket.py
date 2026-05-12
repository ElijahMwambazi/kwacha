from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.basket import BasketItem, BasketItemCreate, BasketItemRead, BasketItemUpdate
from app.models.item import Item
from app.models.price_observation import PriceObservation

router = APIRouter(prefix="/basket", tags=["basket"])


@router.post("", response_model=BasketItemRead, status_code=status.HTTP_201_CREATED)
def add_basket_item(
    payload: BasketItemCreate,
    session: Session = Depends(get_session),
):
    item = session.get(Item, payload.item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    existing_basket_item = session.exec(
        select(BasketItem).where(BasketItem.item_id == payload.item_id)
    ).first()

    if existing_basket_item:
        existing_basket_item.quantity = payload.quantity
        existing_basket_item.unit = payload.unit

        session.add(existing_basket_item)
        session.commit()
        session.refresh(existing_basket_item)

        return existing_basket_item

    basket_item = BasketItem.model_validate(payload)

    session.add(basket_item)
    session.commit()
    session.refresh(basket_item)

    return basket_item


@router.get("", response_model=list[BasketItemRead])
def list_basket_items(
    session: Session = Depends(get_session),
):
    return session.exec(select(BasketItem).order_by(BasketItem.id)).all()


@router.patch("/{basket_item_id}", response_model=BasketItemRead)
def update_basket_item(
    basket_item_id: int,
    payload: BasketItemUpdate,
    session: Session = Depends(get_session),
):
    basket_item = session.get(BasketItem, basket_item_id)

    if not basket_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basket item not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(basket_item, key, value)

    session.add(basket_item)
    session.commit()
    session.refresh(basket_item)

    return basket_item


@router.delete("/{basket_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_basket_item(
    basket_item_id: int,
    session: Session = Depends(get_session),
):
    basket_item = session.get(BasketItem, basket_item_id)

    if not basket_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basket item not found",
        )

    session.delete(basket_item)
    session.commit()

    return None


@router.get("/total")
def get_basket_total(
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    basket_items = session.exec(select(BasketItem)).all()

    lines: list[dict[str, Any]] = []
    total = 0.0

    for basket_item in basket_items:
        item = session.get(Item, basket_item.item_id)

        if not item:
            continue

        latest_price = session.exec(
            select(PriceObservation)
            .where(PriceObservation.item_id == basket_item.item_id)
            .order_by(
                PriceObservation.observed_at.desc(),
                PriceObservation.id.desc(),
            )
        ).first()

        if not latest_price:
            lines.append(
                {
                    "basket_item_id": basket_item.id,
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": basket_item.quantity,
                    "unit": basket_item.unit,
                    "latest_price": None,
                    "price_per_unit": None,
                    "line_total": None,
                    "status": "missing_price",
                }
            )
            continue

        line_total = round(latest_price.price_per_unit * basket_item.quantity, 2)
        total += line_total

        lines.append(
            {
                "basket_item_id": basket_item.id,
                "item_id": item.id,
                "item_name": item.name,
                "quantity": basket_item.quantity,
                "unit": basket_item.unit,
                "latest_price": latest_price.price,
                "price_per_unit": latest_price.price_per_unit,
                "shop_name": latest_price.shop_name,
                "location": latest_price.location,
                "observed_at": latest_price.observed_at,
                "line_total": line_total,
                "status": "priced",
            }
        )

    return {
        "currency": "ZMW",
        "total": round(total, 2),
        "items": lines,
    }