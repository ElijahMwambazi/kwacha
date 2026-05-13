from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, SQLModel, select

from app.database import get_session
from app.models.public_indicator import PublicIndicator

router = APIRouter(prefix="/indicators", tags=["indicators"])


class PublicIndicatorCreate(SQLModel):
    name: str
    value: float
    unit: Optional[str] = None
    source: Optional[str] = None
    observed_at: Optional[datetime] = None


class PublicIndicatorUpdate(SQLModel):
    name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    source: Optional[str] = None
    observed_at: Optional[datetime] = None


@router.post("", status_code=status.HTTP_201_CREATED)
def create_indicator(
    payload: PublicIndicatorCreate,
    session: Session = Depends(get_session),
):
    indicator = PublicIndicator(
        name=payload.name,
        value=payload.value,
        unit=payload.unit,
        source=payload.source,
        observed_at=payload.observed_at or datetime.utcnow(),
    )

    session.add(indicator)
    session.commit()
    session.refresh(indicator)

    return indicator


@router.get("")
def list_indicators(
    name: str | None = Query(default=None),
    session: Session = Depends(get_session),
):
    statement = select(PublicIndicator)

    if name:
        statement = statement.where(PublicIndicator.name == name)

    statement = statement.order_by(
        PublicIndicator.observed_at.desc(),
        PublicIndicator.id.desc(),
    )

    return session.exec(statement).all()


@router.get("/{indicator_id}")
def get_indicator(
    indicator_id: int,
    session: Session = Depends(get_session),
):
    indicator = session.get(PublicIndicator, indicator_id)

    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public indicator not found",
        )

    return indicator


@router.patch("/{indicator_id}")
def update_indicator(
    indicator_id: int,
    payload: PublicIndicatorUpdate,
    session: Session = Depends(get_session),
):
    indicator = session.get(PublicIndicator, indicator_id)

    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public indicator not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(indicator, key, value)

    session.add(indicator)
    session.commit()
    session.refresh(indicator)

    return indicator


@router.delete("/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_indicator(
    indicator_id: int,
    session: Session = Depends(get_session),
):
    indicator = session.get(PublicIndicator, indicator_id)

    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public indicator not found",
        )

    session.delete(indicator)
    session.commit()

    return None