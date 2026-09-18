from pydantic import BaseModel

class MoodQuery(BaseModel):
    mood: str
    limit: int = 10
