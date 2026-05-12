from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class BasketItemBase(SQLModel):
    item_id: int = Field(foreign_key="item.id", index=True)
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="unit")


class BasketItem(BasketItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BasketItemCreate(BasketItemBase):
    pass


class BasketItemRead(BasketItemBase):
    id: int
    created_at: datetime


class BasketItemUpdate(SQLModel):
    quantity: Optional[float] = Field(default=None, gt=0)
    unit: Optional[str] = None