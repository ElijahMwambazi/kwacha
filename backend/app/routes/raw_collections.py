from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, SQLModel, select

from app.database import get_session
from app.models.item import Item
from app.models.price_observation import PriceObservation
from app.models.raw_collection import RawCollection

router = APIRouter(prefix="/raw-collections", tags=["raw collections"])

class RawCollectionCreate(SQLModel):
    item_name: str
    category: str | None = None
    brand: str | None = None
    shop_name: str
    location: str | None = None
    price: float
    quantity: float = 1
    unit: str = "unit"
    source: str | None = None
    notes: str | None = None
    collected_at: datetime | None = None

class RawCollectionUpdate(SQLModel):
    item_name: str | None = None
    category: str | None = None
    brand: str | None = None
    shop_name: str | None = None
    location: str | None = None
    price: float | None = None
    quantity: float | None = None
    unit: str | None = None
    source: str | None = None
    notes: str | None = None
    collected_at: datetime | None = None

def get_or_create_item_from_raw(
    *,
    session: Session,
    raw: RawCollection,
) -> Item:
    item = session.exec(select(Item).where(Item.name == raw.item_name)).first()

    if item:
        return item

    item = Item(
        name=raw.item_name,
        category=raw.category,
        brand=raw.brand,
        default_unit=raw.unit,
    )

    session.add(item)
    session.flush()
    session.refresh(item)

    return item

@router.post("", status_code=status.HTTP_201_CREATED)
def create_raw_collection(
    payload: RawCollectionCreate,
    session: Session = Depends(get_session),
) -> RawCollection:
    raw = RawCollection(
        item_name=payload.item_name,
        category=payload.category,
        brand=payload.brand,
        shop_name=payload.shop_name,
        location=payload.location,
        price=payload.price,
        quantity=payload.quantity,
        unit=payload.unit,
        source=payload.source,
        notes=payload.notes,
        collected_at=payload.collected_at or datetime.utcnow(),
    )

    session.add(raw)
    session.commit()
    session.refresh(raw)

    return raw

@router.get("")
def list_raw_collections(
    status_filter: str | None = Query(default=None, alias="status"),
    session: Session = Depends(get_session),
) -> list[RawCollection]:
    statement = select(RawCollection).order_by(
        RawCollection.created_at.desc(),
        RawCollection.id.desc(),
    )

    if status_filter:
        statement = statement.where(RawCollection.status == status_filter)

    return session.exec(statement).all()

@router.get("/stats")
def get_raw_collection_stats(
    session: Session = Depends(get_session),
) -> dict[str, int]:
    rows = session.exec(select(RawCollection)).all()

    pending_count = sum(1 for row in rows if row.status == "pending")
    approved_count = sum(1 for row in rows if row.status == "approved")
    rejected_count = sum(1 for row in rows if row.status == "rejected")

    return {
        "total_count": len(rows),
        "pending_count": pending_count,
        "approved_count": approved_count,
        "rejected_count": rejected_count,
    }

@router.post("/bulk/approve", status_code=status.HTTP_201_CREATED)
def bulk_approve_raw_collections(
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    pending_rows = session.exec(
        select(RawCollection)
        .where(RawCollection.status == "pending")
        .order_by(RawCollection.id.asc())
    ).all()

    approved_count = 0
    created_items_count = 0
    created_price_observations_count = 0

    for raw in pending_rows:
        existing_item = session.exec(
            select(Item).where(Item.name == raw.item_name)
        ).first()

        item = existing_item

        if not item:
            item = Item(
                name=raw.item_name,
                category=raw.category,
                brand=raw.brand,
                default_unit=raw.unit,
            )
            session.add(item)
            session.flush()
            session.refresh(item)
            created_items_count += 1

        observation = PriceObservation(
            item_id=item.id,
            shop_name=raw.shop_name,
            location=raw.location,
            price=raw.price,
            quantity=raw.quantity,
            unit=raw.unit,
            price_per_unit=round(raw.price / raw.quantity, 4),
            observed_at=raw.collected_at,
        )

        raw.status = "approved"
        raw.reviewed_at = datetime.utcnow()

        session.add(observation)
        session.add(raw)

        approved_count += 1
        created_price_observations_count += 1

    session.commit()

    return {
        "approved_count": approved_count,
        "created_items_count": created_items_count,
        "created_price_observations_count": created_price_observations_count,
    }

@router.post("/bulk/reject")
def bulk_reject_raw_collections(
    session: Session = Depends(get_session),
) -> dict[str, int]:
    pending_rows = session.exec(
        select(RawCollection).where(RawCollection.status == "pending")
    ).all()

    rejected_count = 0

    for raw in pending_rows:
        raw.status = "rejected"
        raw.reviewed_at = datetime.utcnow()

        session.add(raw)
        rejected_count += 1

    session.commit()

    return {
        "rejected_count": rejected_count,
    }

@router.patch("/{raw_collection_id}")
def update_raw_collection(
    raw_collection_id: int,
    payload: RawCollectionUpdate,
    session: Session = Depends(get_session),
) -> RawCollection:
    raw = session.get(RawCollection, raw_collection_id)

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw collection not found",
        )

    if raw.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending raw collections can be updated",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(raw, key, value)

    session.add(raw)
    session.commit()
    session.refresh(raw)

    return raw

@router.post("/{raw_collection_id}/approve", status_code=status.HTTP_201_CREATED)
def approve_raw_collection(
    raw_collection_id: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    raw = session.get(RawCollection, raw_collection_id)

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw collection not found",
        )

    if raw.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending raw collections can be approved",
        )

    item = get_or_create_item_from_raw(session=session, raw=raw)

    observation = PriceObservation(
        item_id=item.id,
        shop_name=raw.shop_name,
        location=raw.location,
        price=raw.price,
        quantity=raw.quantity,
        unit=raw.unit,
        price_per_unit=round(raw.price / raw.quantity, 4),
        observed_at=raw.collected_at,
    )

    raw.status = "approved"
    raw.reviewed_at = datetime.utcnow()

    session.add(observation)
    session.add(raw)
    session.commit()
    session.refresh(observation)
    session.refresh(raw)
    session.refresh(item)

    return {
        "raw_collection": raw.model_dump(mode="json"),
        "item": item.model_dump(mode="json"),
        "price_observation": observation.model_dump(mode="json"),
    }

@router.post("/{raw_collection_id}/reject")
def reject_raw_collection(
    raw_collection_id: int,
    session: Session = Depends(get_session),
) -> RawCollection:
    raw = session.get(RawCollection, raw_collection_id)

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw collection not found",
        )

    if raw.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending raw collections can be rejected",
        )

    raw.status = "rejected"
    raw.reviewed_at = datetime.utcnow()

    session.add(raw)
    session.commit()
    session.refresh(raw)

    return raw

@router.delete("/{raw_collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_raw_collection(
    raw_collection_id: int,
    session: Session = Depends(get_session),
):
    raw = session.get(RawCollection, raw_collection_id)

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Raw collection not found",
        )

    session.delete(raw)
    session.commit()

    return None