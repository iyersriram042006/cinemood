from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class JournalEntryCreate(BaseModel):
    tmdb_id: int
    rating: float
    review: Optional[str] = None
    watched_at: date
    is_rewatch: bool = False
    moods: list[str] = []

class JournalEntryUpdate(BaseModel):
    rating: Optional[float] = None
    review: Optional[str] = None
    watched_at: Optional[date] = None
    is_rewatch: Optional[bool] = None
    moods: Optional[list[str]] = None

class MovieBrief(BaseModel):
    title: str
    poster_path: Optional[str] = None
    genres: Optional[list] = None

    class Config:
        from_attributes = True

class JournalEntryOut(BaseModel):
    id: str
    rating: float
    review: Optional[str] = None
    watched_at: date
    is_rewatch: bool
    created_at: datetime
    movie: MovieBrief
    moods: list[str] = []

    class Config:
        from_attributes = True
