from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Movie, WatchlistItem
from app.schemas.watchlist import WatchlistCreate
from app.services import tmdb_service

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

def _serialize(item: WatchlistItem) -> dict:
    return {
        "id": str(item.id),
        "notes": item.notes,
        "created_at": item.created_at,
        "movie": {
            "tmdb_id": item.movie.tmdb_id,
            "title": item.movie.title,
            "poster_path": item.movie.poster_path,
            "genres": item.movie.genres,
        },
    }

@router.post("")
def add_to_watchlist(data: WatchlistCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.tmdb_id == data.tmdb_id).first()
    if not movie:
        details = tmdb_service.get_movie_details(data.tmdb_id)
        movie = Movie(**details)
        db.add(movie)
        db.flush()

    existing = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id, WatchlistItem.movie_id == movie.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already in watchlist")

    item = WatchlistItem(user_id=user.id, movie_id=movie.id, notes=data.notes)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item)

@router.get("")
def get_watchlist(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    items = db.query(WatchlistItem).filter(WatchlistItem.user_id == user.id).order_by(WatchlistItem.created_at.desc()).all()
    return [_serialize(i) for i in items]

@router.delete("/{item_id}")
def remove_from_watchlist(item_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(WatchlistItem).filter(WatchlistItem.id == item_id, WatchlistItem.user_id == user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"message": "Removed"}
