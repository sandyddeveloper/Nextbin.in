import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

def generate_profile_code():
    return f"STF-{uuid.uuid4().hex[:6].upper()}"

class StaffMaster(BaseModel):
    __tablename__ = "staff_masters"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    profile_code = Column(String, unique=True, index=True, nullable=False, default=generate_profile_code)
    full_name = Column(String, nullable=True)
    designation = Column(String, nullable=True)
    department = Column(String, nullable=True)
    reporting_to_id = Column(Integer, ForeignKey("staff_masters.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="staff_master", lazy="selectin")
    
    # Self-referential relationship for reporting manager hierarchy
    reporting_to = relationship(
        "StaffMaster",
        remote_side="StaffMaster.id",
        backref="subordinates",
        lazy="selectin"
    )
