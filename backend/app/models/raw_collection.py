from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class RawCollection(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: Optional[int] = Field(default=None, foreign_key="datasource.id")
    item_name: str = Field(index=True)
    raw_price: Optional[str] = None
    raw_quantity: Optional[str] = None
    raw_unit: Optional[str] = None
    raw_shop_name: Optional[str] = None
    raw_location: Optional[str] = None
    status: str = Field(default="pending", index=True)
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)