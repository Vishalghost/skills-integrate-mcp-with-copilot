"""
High School Management System API

A FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
from pathlib import Path

from .database.config import get_db
from .database.models import Activity, User
from .auth.security import get_current_user
from .routes import auth, clubs

app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(clubs.router)

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(current_dir, "static")),
    name="static"
)

async def get_or_create_user(email: str, db: AsyncSession) -> User:
    """Get or create a user by email."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(email=email, role="student")
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

@app.get("/activities")
async def get_activities(db: AsyncSession = Depends(get_db)):
    """Get all activities with their participants."""
    result = await db.execute(select(Activity))
    activities = result.scalars().all()
    
    return [{
        "name": activity.name,
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "club": activity.club.name if activity.club else None,
        "participants": [p.email for p in activity.participants]
    } for activity in activities]

@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(
    activity_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign up a student for an activity."""
    # Get activity
    result = await db.execute(select(Activity).where(Activity.name == activity_name))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if activity is part of a club
    if activity.club:
        # Check if user is a member of the club
        is_member = any(
            member.user_id == current_user.id
            for member in activity.club.members
            if member.status == "active"
        )
        if not is_member and current_user.role == "student":
            raise HTTPException(
                status_code=403,
                detail="You must be a club member to join this activity"
            )
    
    # Check if user is already signed up
    if current_user in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="You are already signed up"
        )
    
    # Check max participants
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )
    
    # Add student to activity
    activity.participants.append(current_user)
    await db.commit()
    
    return {"message": f"Signed up for {activity_name}"}

@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(
    activity_name: str,
    user_email: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unregister from an activity. Teachers/admins can unregister others."""
    # Get activity
    result = await db.execute(select(Activity).where(Activity.name == activity_name))
    activity = result.scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Determine target user
    target_user = current_user
    if user_email and current_user.role in ["teacher", "admin"]:
        result = await db.execute(select(User).where(User.email == user_email))
        target_user = result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
    elif user_email:
        raise HTTPException(
            status_code=403,
            detail="Only teachers and admins can unregister other users"
        )
    
    # Check if user is signed up
    if target_user not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Not signed up for this activity"
        )
    
    # Remove from activity
    activity.participants.remove(target_user)
    await db.commit()
    
    return {
        "message": (
            f"Unregistered {target_user.email} from {activity_name}"
            if user_email else
            f"Unregistered from {activity_name}"
        )
    }
