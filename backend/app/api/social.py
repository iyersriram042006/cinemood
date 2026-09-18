from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, JournalEntry, Like, Comment
from app.schemas.social import CommentCreate

router = APIRouter(prefix="/api/social", tags=["social"])

@router.post("/entries/{entry_id}/like")
def like_entry(entry_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    existing = db.query(Like).filter(Like.journal_entry_id == entry_id, Like.user_id == user.id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {"liked": False}

    like = Like(user_id=user.id, journal_entry_id=entry_id)
    db.add(like)
    db.commit()
    return {"liked": True}

@router.post("/entries/{entry_id}/comments")
def add_comment(entry_id: str, data: CommentCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    comment = Comment(user_id=user.id, journal_entry_id=entry_id, text=data.text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": str(comment.id), "text": comment.text, "user_name": user.name, "created_at": comment.created_at}

@router.get("/entries/{entry_id}/comments")
def get_comments(entry_id: str, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.journal_entry_id == entry_id).order_by(Comment.created_at).all()
    return [{"id": str(c.id), "text": c.text, "user_name": c.user.name, "created_at": c.created_at} for c in comments]

@router.get("/users/{user_id}/journal")
def public_journal(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == user_id).order_by(JournalEntry.watched_at.desc()).all()

    result = []
    for e in entries:
        like_count = db.query(Like).filter(Like.journal_entry_id == e.id).count()
        comment_count = db.query(Comment).filter(Comment.journal_entry_id == e.id).count()
        liked_by_me = db.query(Like).filter(Like.journal_entry_id == e.id, Like.user_id == current_user.id).first() is not None
        result.append({
            "id": str(e.id),
            "title": e.movie.title,
            "poster_path": e.movie.poster_path,
            "rating": float(e.rating),
            "review": e.review,
            "watched_at": str(e.watched_at),
            "moods": [m.name for m in e.moods],
            "like_count": like_count,
            "comment_count": comment_count,
            "liked_by_me": liked_by_me,
        })
    return result
