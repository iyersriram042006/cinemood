import re
from sqlalchemy.orm import Session
from app.models.models import JournalEntry

STOPWORDS = {
    "i", "am", "is", "are", "want", "kuch", "hai", "hua", "chahiye", "a", "an",
    "the", "to", "for", "and", "something", "some", "need", "feeling", "feel",
    "mai", "mujhe", "ho", "ka", "ki", "ke", "bhi", "toh", "aaj"
}

def _extract_keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}

def get_recommendations(db: Session, user_id, mood_text: str, limit: int = 10):
    keywords = _extract_keywords(mood_text)

    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).all()

    scored = []
    for entry in entries:
        score = 0.0
        matched_reasons = []

        mood_names = {m.name.lower() for m in entry.moods}
        mood_words = set()
        for m in mood_names:
            mood_words |= set(m.replace("-", " ").split())

        mood_overlap = keywords & mood_words
        if mood_overlap:
            score += 0.5 * len(mood_overlap)
            matched_reasons.append(f"tagged as {', '.join(entry.moods and [m.name for m in entry.moods] or [])}")

        review_text = (entry.review or "").lower()
        review_words = set(re.findall(r"[a-zA-Z]+", review_text))
        review_overlap = keywords & review_words
        if review_overlap:
            score += 0.3 * len(review_overlap)
            matched_reasons.append("your review mentioned similar words")

        genre_words = set()
        for g in (entry.movie.genres or []):
            genre_words |= set(g.lower().split())
        genre_overlap = keywords & genre_words
        if genre_overlap:
            score += 0.2 * len(genre_overlap)
            matched_reasons.append(f"genre match: {', '.join(genre_overlap)}")

        rating_boost = float(entry.rating) / 5.0 * 0.3
        score += rating_boost

        if score > 0:
            scored.append({
                "movie_id": str(entry.movie.id),
                "title": entry.movie.title,
                "poster_path": entry.movie.poster_path,
                "rating": float(entry.rating),
                "moods": [m.name for m in entry.moods],
                "score": round(score, 3),
                "reason": "; ".join(matched_reasons) if matched_reasons else "matched your general taste",
            })

    scored.sort(key=lambda x: x["score"], reverse=True)

    if not scored:
        return _fallback_top_rated(db, user_id, limit)

    return scored[:limit]

def _fallback_top_rated(db: Session, user_id, limit: int):
    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id)
        .order_by(JournalEntry.rating.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "movie_id": str(e.movie.id),
            "title": e.movie.title,
            "poster_path": e.movie.poster_path,
            "rating": float(e.rating),
            "moods": [m.name for m in e.moods],
            "score": 0.0,
            "reason": "no direct mood match — showing your top-rated movies instead",
        }
        for e in entries
    ]
