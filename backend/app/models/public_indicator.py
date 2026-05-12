from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PublicIndicator(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    value: float
    unit: Optional[str] = None
    source: Optional[str] = None
    observed_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)