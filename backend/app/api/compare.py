from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, JournalEntry

router = APIRouter(prefix="/api/compare", tags=["compare"])

@router.get("/{other_user_id}")
def compare_taste(other_user_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    other = db.query(User).filter(User.id == other_user_id).first()
    if not other:
        raise HTTPException(status_code=404, detail="User not found")

    my_entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()
    their_entries = db.query(JournalEntry).filter(JournalEntry.user_id == other_user_id).all()

    my_movies = {e.movie.tmdb_id: e for e in my_entries}
    their_movies = {e.movie.tmdb_id: e for e in their_entries}

    shared_ids = set(my_movies.keys()) & set(their_movies.keys())
    shared_movies = []
    you_rated_higher = []
    they_rated_higher = []

    for tmdb_id in shared_ids:
        my_e = my_movies[tmdb_id]
        their_e = their_movies[tmdb_id]
        shared_movies.append({
            "title": my_e.movie.title,
            "your_rating": float(my_e.rating),
            "their_rating": float(their_e.rating),
        })
        if float(my_e.rating) > float(their_e.rating):
            you_rated_higher.append(my_e.movie.title)
        elif float(their_e.rating) > float(my_e.rating):
            they_rated_higher.append(my_e.movie.title)

    def genre_counts(entries):
        counts = {}
        for e in entries:
            for g in (e.movie.genres or []):
                counts[g] = counts.get(g, 0) + 1
        return counts

    my_genres = genre_counts(my_entries)
    their_genres = genre_counts(their_entries)
    all_genres = set(my_genres.keys()) | set(their_genres.keys())
    genre_overlap = [
        {"genre": g, "your_count": my_genres.get(g, 0), "their_count": their_genres.get(g, 0)}
        for g in all_genres
    ]
    genre_overlap.sort(key=lambda x: x["your_count"] + x["their_count"], reverse=True)

    return {
        "shared_movie_count": len(shared_movies),
        "shared_movies": shared_movies,
        "you_rated_higher": you_rated_higher,
        "they_rated_higher": they_rated_higher,
        "genre_overlap": genre_overlap[:10],
    }
