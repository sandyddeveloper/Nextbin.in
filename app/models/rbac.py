from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base

# Association table for User-Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)

# Association table for Role-Permission (Many-to-Many)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
)

class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String, nullable=False)
    codename = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        backref="roles",
        lazy="selectin"
    )
    
    # Self-referential relationship for hierarchy
    parent = relationship(
        "Role",
        remote_side="Role.id",
        backref="children",
        lazy="selectin"
    )
