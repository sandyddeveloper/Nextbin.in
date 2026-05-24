from sqlalchemy import Column, String, JSON
from app.models.base import BaseModel

class NilagravityKV(BaseModel):
    __tablename__ = "nilagravity_kv"

    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
