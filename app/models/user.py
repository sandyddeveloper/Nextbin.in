from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Relationships
    roles = relationship(
        "Role",
        secondary="user_roles",
        backref="users",
        lazy="selectin"
    )
    
    staff_master = relationship(
        "StaffMaster",
        back_populates="user",
        uselist=False,
        lazy="selectin"
    )

    @property
    def role_names(self) -> list[str]:
        """
        Returns a list of all role names assigned to this user.
        """
        # If user is superuser, implicitly include SUPER_ADMIN if not already present
        names = [role.name for role in self.roles]
        if self.is_superuser and "SUPER_ADMIN" not in names:
            names.append("SUPER_ADMIN")
        return names

    @property
    def user_code(self) -> str:
        """
        Returns a unique public identifier for the user.
        """
        return f"USR-{self.id:06d}"
