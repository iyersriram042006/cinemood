from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def generate_embedding(text: str):
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()

def build_embedding_text(movie_title: str, genres: list, moods: list, review: str) -> str:
    mood_text = ", ".join(moods) if moods else "unspecified"
    genre_text = ", ".join(genres) if genres else "unspecified"
    review_text = review or ""
    return f"Movie: {movie_title}. Genres: {genre_text}. Mood: {mood_text}. Review: {review_text}".strip()
