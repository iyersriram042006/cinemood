from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User
from app.schemas.recommendation import MoodQuery
from app.services.recommendation_service import get_recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

@router.post("")
def recommend(query: MoodQuery, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    results = get_recommendations(db, user.id, query.mood, query.limit)
    return {"query": query.mood, "recommendations": results}
