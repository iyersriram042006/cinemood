from app.core.database import SessionLocal
from app.models.models import JournalEntry
from app.services.embedding_service import generate_embedding, build_embedding_text

db = SessionLocal()
entries = db.query(JournalEntry).filter(JournalEntry.embedding.is_(None)).all()

print(f"Backfilling {len(entries)} entries...")

for entry in entries:
    text = build_embedding_text(
        entry.movie.title, entry.movie.genres or [], [m.name for m in entry.moods], entry.review
    )
    entry.embedding_text = text
    entry.embedding = generate_embedding(text)

db.commit()
db.close()
print("Done!")
