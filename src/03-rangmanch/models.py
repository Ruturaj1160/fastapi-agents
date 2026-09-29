from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    play_name: str = Field(index=True)  # we can search using this
    reviewer_name: str
    rating: int = Field(ge=1, le=5)  # greater than 1 and less then 5
    comment: str
    created_at: datetime = Field(default_factory=datetime.now)
