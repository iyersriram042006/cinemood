from pydantic import BaseModel
from typing import Optional

class WatchlistCreate(BaseModel):
    tmdb_id: int
    notes: Optional[str] = None
