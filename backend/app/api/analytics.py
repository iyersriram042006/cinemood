from collections import Counter
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, JournalEntry

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    if not entries:
        return {"total_movies": 0, "movies_this_year": 0, "average_rating": 0, "rewatches": 0}

    current_year = datetime.now().year
    movies_this_year = sum(1 for e in entries if e.watched_at.year == current_year)
    avg_rating = sum(float(e.rating) for e in entries) / len(entries)
    rewatches = sum(1 for e in entries if e.is_rewatch)

    return {
        "total_movies": len(entries),
        "movies_this_year": movies_this_year,
        "average_rating": round(avg_rating, 2),
        "rewatches": rewatches,
    }

@router.get("/genres")
def genres(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    genre_ratings = {}
    for e in entries:
        for g in (e.movie.genres or []):
            genre_ratings.setdefault(g, []).append(float(e.rating))

    result = [
        {"genre": g, "count": len(ratings), "average_rating": round(sum(ratings) / len(ratings), 2)}
        for g, ratings in genre_ratings.items()
    ]
    return sorted(result, key=lambda x: x["count"], reverse=True)

@router.get("/directors")
def directors(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    counter = Counter()
    for e in entries:
        for d in (e.movie.directors or []):
            counter[d] += 1

    return [{"director": name, "count": count} for name, count in counter.most_common(10)]

@router.get("/ratings")
def ratings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    distribution = Counter(float(e.rating) for e in entries)
    return sorted([{"rating": r, "count": c} for r, c in distribution.items()], key=lambda x: x["rating"])

@router.get("/timeline")
def timeline(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    monthly = Counter(e.watched_at.strftime("%Y-%m") for e in entries)
    return sorted([{"month": m, "count": c} for m, c in monthly.items()], key=lambda x: x["month"])

@router.get("/summary")
def taste_summary(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user.id).all()

    if not entries:
        return {"summary": "Log a few movies to see your taste summary."}

    genre_ratings = {}
    for e in entries:
        for g in (e.movie.genres or []):
            genre_ratings.setdefault(g, []).append(float(e.rating))

    top_genres = sorted(genre_ratings.items(), key=lambda x: len(x[1]), reverse=True)[:2]
    genre_text = " and ".join(g for g, _ in top_genres) if top_genres else "a mix of genres"
    avg_rating = round(sum(float(e.rating) for e in entries) / len(entries), 2)

    summary = (
        f"You've watched {len(entries)} movies, with {genre_text} making up most of your viewing. "
        f"Your average rating is {avg_rating}/5, "
        f"{'suggesting you are quite selective' if avg_rating < 3.8 else 'showing you generally enjoy what you watch'}."
    )
    return {"summary": summary}
