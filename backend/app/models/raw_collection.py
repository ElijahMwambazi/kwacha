from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RawCollection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    item_name: str = Field(index=True)
    category: Optional[str] = Field(default=None, index=True)
    brand: Optional[str] = None

    shop_name: str = Field(index=True)
    location: Optional[str] = Field(default=None, index=True)

    price: float = Field(gt=0)
    quantity: float = Field(default=1, gt=0)
    unit: str = Field(default="unit")

    source: Optional[str] = None
    notes: Optional[str] = None

    status: str = Field(default="pending", index=True)
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)