from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class DataSource(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    source_type: str = Field(default="manual", index=True)
    url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)