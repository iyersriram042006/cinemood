import re
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.models import JournalEntry
from app.services.embedding_service import generate_embedding

def get_recommendations(db: Session, user_id, mood_text: str, limit: int = 10):
    query_embedding = generate_embedding(mood_text)

    # pgvector cosine distance: smaller = more similar
    candidates = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == user_id, JournalEntry.embedding.isnot(None))
        .order_by(JournalEntry.embedding.cosine_distance(query_embedding))
        .limit(30)
        .all()
    )

    if not candidates:
        return _fallback_top_rated(db, user_id, limit)

    scored = []
    for entry in candidates:
        distance = _cosine_distance(entry.embedding, query_embedding)
        semantic_similarity = 1 - distance
        rating_signal = float(entry.rating) / 5.0

        final_score = semantic_similarity

        scored.append({
            "movie_id": str(entry.movie.id),
            "title": entry.movie.title,
            "poster_path": entry.movie.poster_path,
            "rating": float(entry.rating),
            "moods": [m.name for m in entry.moods],
            "score": round(final_score, 3),
            "semantic_similarity": round(semantic_similarity, 3),
            "reason": _build_reason(entry, semantic_similarity),
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]

def _cosine_distance(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return 1 - (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))

def _build_reason(entry, similarity):
    if similarity > 0.6:
        mood_str = ", ".join(m.name for m in entry.moods) if entry.moods else "your notes"
        return f"strong match to how you described this ({mood_str})"
    elif similarity > 0.4:
        return "somewhat matches the mood you described"
    else:
        return "matched based on your overall taste"

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
            "reason": "no logged movies with mood data yet — showing your top-rated instead",
        }
        for e in entries
    ]
