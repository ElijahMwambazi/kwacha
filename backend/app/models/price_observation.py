from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PriceObservationBase(SQLModel):
    item_id: int = Field(foreign_key="item.id", index=True)
    shop_name: str = Field(index=True)
    location: Optional[str] = Field(default=None, index=True)
    price: float = Field(gt=0)
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="unit")
    observed_at: datetime = Field(default_factory=datetime.utcnow)


class PriceObservation(PriceObservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    price_per_unit: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PriceObservationCreate(PriceObservationBase):
    pass


class PriceObservationRead(PriceObservationBase):
    id: int
    price_per_unit: float
    created_at: datetime


class PriceObservationUpdate(SQLModel):
    item_id: Optional[int] = None
    shop_name: Optional[str] = None
    location: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None
    observed_at: Optional[datetime] = None