from pydantic import BaseModel
from typing import Optional

class MovieSearchResult(BaseModel):
    tmdb_id: int
    title: str
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    vote_average: Optional[float] = None
    overview: Optional[str] = None

class MovieOut(BaseModel):
    id: str
    tmdb_id: int
    title: str
    poster_path: Optional[str] = None
    release_date: Optional[str] = None
    genres: Optional[list] = None
    directors: Optional[list] = None

    class Config:
        from_attributes = True
