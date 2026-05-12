from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.item import Item
from app.models.price_observation import (
    PriceObservation,
    PriceObservationCreate,
    PriceObservationRead,
    PriceObservationUpdate,
)

router = APIRouter(prefix="/prices", tags=["prices"])


def calculate_price_per_unit(price: float, quantity: float) -> float:
    return round(price / quantity, 4)


@router.post("", response_model=PriceObservationRead, status_code=status.HTTP_201_CREATED)
def create_price_observation(
    payload: PriceObservationCreate,
    session: Session = Depends(get_session),
):
    item = session.get(Item, payload.item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    observation = PriceObservation(
        **payload.model_dump(),
        price_per_unit=calculate_price_per_unit(payload.price, payload.quantity),
    )

    session.add(observation)
    session.commit()
    session.refresh(observation)

    return observation


@router.get("", response_model=list[PriceObservationRead])
def list_price_observations(
    item_id: int | None = Query(default=None),
    session: Session = Depends(get_session),
):
    statement = select(PriceObservation)

    if item_id is not None:
        statement = statement.where(PriceObservation.item_id == item_id)

    statement = statement.order_by(PriceObservation.observed_at.desc())

    return session.exec(statement).all()


@router.get("/{price_id}", response_model=PriceObservationRead)
def get_price_observation(
    price_id: int,
    session: Session = Depends(get_session),
):
    observation = session.get(PriceObservation, price_id)

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price observation not found",
        )

    return observation


@router.patch("/{price_id}", response_model=PriceObservationRead)
def update_price_observation(
    price_id: int,
    payload: PriceObservationUpdate,
    session: Session = Depends(get_session),
):
    observation = session.get(PriceObservation, price_id)

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price observation not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "item_id" in update_data:
        item = session.get(Item, update_data["item_id"])

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item not found",
            )

    for key, value in update_data.items():
        setattr(observation, key, value)

    observation.price_per_unit = calculate_price_per_unit(
        observation.price,
        observation.quantity,
    )

    session.add(observation)
    session.commit()
    session.refresh(observation)

    return observation


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_price_observation(
    price_id: int,
    session: Session = Depends(get_session),
):
    observation = session.get(PriceObservation, price_id)

    if not observation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Price observation not found",
        )

    session.delete(observation)
    session.commit()

    return None