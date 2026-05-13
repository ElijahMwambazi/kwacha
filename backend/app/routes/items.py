
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.basket import BasketItem
from app.models.item import Item, ItemCreate, ItemRead, ItemUpdate
from app.models.price_observation import PriceObservation

router = APIRouter(prefix="/items", tags=["items"])


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    session: Session = Depends(get_session),
):
    item = Item.model_validate(payload)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("", response_model=list[ItemRead])
def list_items(
    session: Session = Depends(get_session),
):
    return session.exec(select(Item).order_by(Item.name)).all()


@router.get("/{item_id}", response_model=ItemRead)
def get_item(
    item_id: int,
    session: Session = Depends(get_session),
):
    item = session.get(Item, item_id)

    if not item:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Item not found",
      )

    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    session: Session = Depends(get_session),
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(item, key, value)

    session.add(item)
    session.commit()
    session.refresh(item)

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    session: Session = Depends(get_session),
):
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    basket_items = session.exec(
        select(BasketItem).where(BasketItem.item_id == item_id)
    ).all()

    price_observations = session.exec(
        select(PriceObservation).where(PriceObservation.item_id == item_id)
    ).all()

    for basket_item in basket_items:
        session.delete(basket_item)

    for price_observation in price_observations:
        session.delete(price_observation)

    session.delete(item)
    session.commit()

    return None