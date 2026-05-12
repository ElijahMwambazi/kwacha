from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    name: str = Field(index=True)
    category: Optional[str] = Field(default=None, index=True)
    brand: Optional[str] = None
    default_unit: str = Field(default="unit")


class Item(ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ItemCreate(ItemBase):
    pass


class ItemRead(ItemBase):
    id: int
    created_at: datetime


class ItemUpdate(SQLModel):
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    default_unit: Optional[str] = None