from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ModelTrainingRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_name: str = Field(index=True)
    model_type: str = Field(index=True)
    target: str
    training_rows: int
    mae: Optional[float] = None
    r2: Optional[float] = None
    model_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)