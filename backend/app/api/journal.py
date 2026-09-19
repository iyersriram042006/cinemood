from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Movie, MoodTag, JournalEntry
from app.schemas.journal import JournalEntryCreate, JournalEntryUpdate, JournalEntryOut
from app.services import tmdb_service
from app.services.embedding_service import generate_embedding, build_embedding_text

router = APIRouter(prefix="/api/journal", tags=["journal"])

def _get_or_create_moods(db: Session, mood_names: list[str]) -> list[MoodTag]:
    moods = []
    for name in mood_names:
        name = name.strip().lower()
        if not name:
            continue
        mood = db.query(MoodTag).filter(MoodTag.name == name).first()
        if not mood:
            mood = MoodTag(name=name)
            db.add(mood)
            db.flush()
        moods.append(mood)
    return moods

def _serialize(entry: JournalEntry) -> dict:
    return {
        "id": str(entry.id),
        "rating": float(entry.rating),
        "review": entry.review,
        "watched_at": entry.watched_at,
        "is_rewatch": entry.is_rewatch,
        "created_at": entry.created_at,
        "movie": entry.movie,
        "moods": [m.name for m in entry.moods],
    }

@router.post("", response_model=JournalEntryOut)
def create_entry(data: JournalEntryCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.tmdb_id == data.tmdb_id).first()
    if not movie:
        details = tmdb_service.get_movie_details(data.tmdb_id)
        movie = Movie(**details)
        db.add(movie)
        db.flush()

    moods = _get_or_create_moods(db, data.moods)

    embedding_text = build_embedding_text(
        movie.title, movie.genres or [], [m.name for m in moods], data.review
    )
    embedding = generate_embedding(embedding_text)

    entry = JournalEntry(
        user_id=user.id,
        movie_id=movie.id,
        rating=data.rating,
        review=data.review,
        watched_at=data.watched_at,
        is_rewatch=data.is_rewatch,
        moods=moods,
        embedding_text=embedding_text,
        embedding=embedding,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _serialize(entry)

@router.get("", response_model=list[JournalEntryOut])
def get_journal(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    search: str = None,
    genre: str = None,
    mood: str = None,
    min_rating: float = None,
    sort: str = "date_desc",
):
    query = db.query(JournalEntry).filter(JournalEntry.user_id == user.id)
    entries = query.all()

    if search:
        s = search.lower()
        entries = [e for e in entries if s in e.movie.title.lower()]
    if genre:
        entries = [e for e in entries if genre in (e.movie.genres or [])]
    if mood:
        entries = [e for e in entries if mood in [m.name for m in e.moods]]
    if min_rating is not None:
        entries = [e for e in entries if float(e.rating) >= min_rating]

    if sort == "date_asc":
        entries.sort(key=lambda e: e.watched_at)
    elif sort == "rating_desc":
        entries.sort(key=lambda e: float(e.rating), reverse=True)
    elif sort == "rating_asc":
        entries.sort(key=lambda e: float(e.rating))
    else:
        entries.sort(key=lambda e: e.watched_at, reverse=True)

    return [_serialize(e) for e in entries]

@router.put("/{entry_id}", response_model=JournalEntryOut)
def update_entry(entry_id: str, data: JournalEntryUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id, JournalEntry.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if data.rating is not None:
        entry.rating = data.rating
    if data.review is not None:
        entry.review = data.review
    if data.watched_at is not None:
        entry.watched_at = data.watched_at
    if data.is_rewatch is not None:
        entry.is_rewatch = data.is_rewatch
    if data.moods is not None:
        entry.moods = _get_or_create_moods(db, data.moods)

    if data.review is not None or data.moods is not None:
        embedding_text = build_embedding_text(
            entry.movie.title, entry.movie.genres or [], [m.name for m in entry.moods], entry.review
        )
        entry.embedding_text = embedding_text
        entry.embedding = generate_embedding(embedding_text)

    db.commit()
    db.refresh(entry)
    return _serialize(entry)

@router.delete("/{entry_id}")
def delete_entry(entry_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id, JournalEntry.user_id == user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Deleted"}
