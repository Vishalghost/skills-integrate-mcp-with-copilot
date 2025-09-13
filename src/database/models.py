"""Database models for the application."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .config import Base

# Association table for activity participants
activity_participants = Table(
    'activity_participants',
    Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    """User model for students, teachers, and administrators."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50))  # student, teacher, admin
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    activities: Mapped[List["Activity"]] = relationship(
        secondary=activity_participants,
        back_populates="participants"
    )
    clubs_leading: Mapped[List["Club"]] = relationship(
        "Club",
        back_populates="leader",
        foreign_keys="[Club.leader_id]"
    )
    clubs_membership: Mapped[List["ClubMember"]] = relationship(
        "ClubMember",
        back_populates="user"
    )

class Activity(Base):
    """Activity model for school activities and clubs."""
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(1000))
    schedule: Mapped[str] = mapped_column(String(255))
    max_participants: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    participants: Mapped[List[User]] = relationship(
        secondary=activity_participants,
        back_populates="activities"
    )
    club_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clubs.id"))
    club: Mapped[Optional["Club"]] = relationship(back_populates="activities")

class ClubRole(Base):
    """Roles within a club."""
    __tablename__ = "club_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(255))
    permissions: Mapped[str] = mapped_column(String(1000))  # JSON string of permissions
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"))

    # Relationships
    club: Mapped["Club"] = relationship(back_populates="roles")
    members: Mapped[List["ClubMember"]] = relationship(back_populates="role")

class ClubMember(Base):
    """Association model for club memberships with roles."""
    __tablename__ = "club_members"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"))
    role_id: Mapped[int] = mapped_column(ForeignKey("club_roles.id"))
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(50))  # active, inactive, pending

    # Relationships
    user: Mapped[User] = relationship(back_populates="clubs_membership")
    club: Mapped["Club"] = relationship(back_populates="members")
    role: Mapped[ClubRole] = relationship(back_populates="members")

class Club(Base):
    """Club model for organizing related activities."""
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(1000))
    category: Mapped[str] = mapped_column(String(100))
    max_members: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )

    # Relationships
    activities: Mapped[List[Activity]] = relationship(back_populates="club")
    leader_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    leader: Mapped[Optional[User]] = relationship(
        foreign_keys=[leader_id],
        back_populates="clubs_leading"
    )
    members: Mapped[List[ClubMember]] = relationship(back_populates="club")
    roles: Mapped[List[ClubRole]] = relationship(back_populates="club")
    budget_entries: Mapped[List["ClubBudget"]] = relationship(back_populates="club")

class ClubBudget(Base):
    """Budget tracking for clubs."""
    __tablename__ = "club_budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"))
    amount: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column(String(1000))
    type: Mapped[str] = mapped_column(String(50))  # income, expense
    category: Mapped[str] = mapped_column(String(100))
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    club: Mapped[Club] = relationship(back_populates="budget_entries")
    created_by: Mapped[User] = relationship()