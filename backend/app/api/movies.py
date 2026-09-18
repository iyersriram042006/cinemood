from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Movie
from app.schemas.movie import MovieSearchResult
from app.services import tmdb_service

router = APIRouter(prefix="/api/movies", tags=["movies"])

@router.get("/search", response_model=list[MovieSearchResult])
def search_movies(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    return tmdb_service.search_movies(query)

@router.post("/{tmdb_id}")
def add_movie(tmdb_id: int, db: Session = Depends(get_db)):
    existing = db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first()
    if existing:
        return existing

    details = tmdb_service.get_movie_details(tmdb_id)
    movie = Movie(**details)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    return movie
