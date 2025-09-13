"""Club management API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from datetime import datetime

from ..auth.audit import audit_log_middleware

from ..database.config import get_db
from ..database.models import Club, User, ClubMember, ClubRole, ClubBudget
from ..auth.security import get_current_user, check_permission

router = APIRouter(prefix="/clubs", tags=["clubs"])

# Pydantic models for request/response
class ClubBase(BaseModel):
    name: str
    description: str
    category: str
    max_members: Optional[int] = None

class ClubCreate(ClubBase):
    pass

class ClubUpdate(ClubBase):
    is_active: Optional[bool] = None

class ClubMemberAdd(BaseModel):
    email: EmailStr
    role_name: str

class BudgetEntry(BaseModel):
    amount: float
    description: str
    type: str
    category: str

# API endpoints
@router.post("/", response_model=dict)
@audit_log_middleware(action="create", entity_type="club")
async def create_club(
    club: ClubCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_permission(["admin", "teacher"]))
):
    """Create a new club."""
    new_club = Club(
        name=club.name,
        description=club.description,
        category=club.category,
        max_members=club.max_members,
        leader_id=current_user.id
    )
    db.add(new_club)
    await db.commit()
    await db.refresh(new_club)

    # Create default club roles
    default_roles = [
        {
            "name": "Leader",
            "description": "Club leader with full permissions",
            "permissions": "all"
        },
        {
            "name": "Member",
            "description": "Regular club member",
            "permissions": "view,participate"
        }
    ]

    for role_data in default_roles:
        role = ClubRole(
            name=role_data["name"],
            description=role_data["description"],
            permissions=role_data["permissions"],
            club_id=new_club.id
        )
        db.add(role)

    # Add creator as leader
    leader_role = await db.execute(
        select(ClubRole)
        .where(ClubRole.club_id == new_club.id)
        .where(ClubRole.name == "Leader")
    )
    leader_role = leader_role.scalar_one()
    member = ClubMember(
        user_id=current_user.id,
        club_id=new_club.id,
        role_id=leader_role.id,
        status="active"
    )
    db.add(member)
    await db.commit()

    return {"message": "Club created successfully", "id": new_club.id}

@router.get("/", response_model=List[dict])
async def list_clubs(
    category: Optional[str] = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """List all clubs with optional filtering."""
    query = select(Club).where(Club.is_active == is_active)
    if category:
        query = query.where(Club.category == category)
    
    result = await db.execute(query)
    clubs = result.scalars().all()
    
    return [{
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "category": club.category,
        "max_members": club.max_members,
        "member_count": len(club.members),
        "leader": {
            "id": club.leader.id,
            "email": club.leader.email,
            "name": f"{club.leader.first_name} {club.leader.last_name}"
        } if club.leader else None
    } for club in clubs]

@router.post("/{club_id}/members")
async def add_club_member(
    club_id: int,
    member: ClubMemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_permission(["admin", "teacher"]))
):
    """Add a member to a club."""
    # Check if club exists and is active
    club = await db.get(Club, club_id)
    if not club or not club.is_active:
        raise HTTPException(status_code=404, detail="Club not found")

    # Check member limit
    if club.max_members and len(club.members) >= club.max_members:
        raise HTTPException(status_code=400, detail="Club is at maximum capacity")

    # Get or create user
    result = await db.execute(
        select(User).where(User.email == member.email)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    result = await db.execute(
        select(ClubMember)
        .where(ClubMember.club_id == club_id)
        .where(ClubMember.user_id == user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this club"
        )

    # Get role
    result = await db.execute(
        select(ClubRole)
        .where(ClubRole.club_id == club_id)
        .where(ClubRole.name == member.role_name)
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Add member
    member = ClubMember(
        user_id=user.id,
        club_id=club_id,
        role_id=role.id,
        status="active"
    )
    db.add(member)
    await db.commit()

    return {"message": "Member added successfully"}

@router.post("/{club_id}/budget")
async def add_budget_entry(
    club_id: int,
    entry: BudgetEntry,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(check_permission(["admin", "teacher"]))
):
    """Add a budget entry for a club."""
    # Check if club exists and is active
    club = await db.get(Club, club_id)
    if not club or not club.is_active:
        raise HTTPException(status_code=404, detail="Club not found")

    # Create budget entry
    budget_entry = ClubBudget(
        club_id=club_id,
        amount=entry.amount,
        description=entry.description,
        type=entry.type,
        category=entry.category,
        created_by_id=current_user.id
    )
    db.add(budget_entry)
    await db.commit()

    return {"message": "Budget entry added successfully"}