from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FriendRequestCreate(BaseModel):
    addressee_email: str

class FriendshipOut(BaseModel):
    id: str
    status: str
    other_user_name: Optional[str] = None
    other_user_email: str

class CommentCreate(BaseModel):
    text: str

class CommentOut(BaseModel):
    id: str
    text: str
    user_name: Optional[str] = None
    created_at: datetime

class PublicJournalEntry(BaseModel):
    id: str
    title: str
    poster_path: Optional[str] = None
    rating: float
    review: Optional[str] = None
    watched_at: str
    moods: list[str] = []
    like_count: int = 0
    comment_count: int = 0
    liked_by_me: bool = False
