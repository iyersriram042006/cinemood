from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api import auth, movies, journal, analytics, recommendations, friends, social, compare

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CineMood API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://cinemood-frontend.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(journal.router)
app.include_router(analytics.router)
app.include_router(recommendations.router)
app.include_router(friends.router)
app.include_router(social.router)
app.include_router(compare.router)

@app.get("/")
def root():
    return {"message": "CineMood API running"}
