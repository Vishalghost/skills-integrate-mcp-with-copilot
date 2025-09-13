"""Initial data migration

Revision ID: 002_initial_data
Create Date: 2025-09-13
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = '002_initial_data'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Initial activities data
    activities = [
        {
            "name": "Chess Club",
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12
        },
        {
            "name": "Programming Class",
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20
        },
        {
            "name": "Gym Class",
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30
        },
        {
            "name": "Soccer Team",
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22
        },
        {
            "name": "Basketball Team",
            "description": "Practice and play basketball with the school team",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15
        },
        {
            "name": "Art Club",
            "description": "Explore your creativity through painting and drawing",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15
        },
        {
            "name": "Drama Club",
            "description": "Act, direct, and produce plays and performances",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 20
        },
        {
            "name": "Math Club",
            "description": "Solve challenging problems and participate in math competitions",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10
        },
        {
            "name": "Debate Team",
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 12
        }
    ]

    # Initial users data
    users = [
        {"email": "michael@mergington.edu", "role": "student"},
        {"email": "daniel@mergington.edu", "role": "student"},
        {"email": "emma@mergington.edu", "role": "student"},
        {"email": "sophia@mergington.edu", "role": "student"},
        {"email": "john@mergington.edu", "role": "student"},
        {"email": "olivia@mergington.edu", "role": "student"},
        {"email": "liam@mergington.edu", "role": "student"},
        {"email": "noah@mergington.edu", "role": "student"},
        {"email": "ava@mergington.edu", "role": "student"},
        {"email": "mia@mergington.edu", "role": "student"},
        {"email": "amelia@mergington.edu", "role": "student"},
        {"email": "harper@mergington.edu", "role": "student"},
        {"email": "ella@mergington.edu", "role": "student"},
        {"email": "scarlett@mergington.edu", "role": "student"},
        {"email": "james@mergington.edu", "role": "student"},
        {"email": "benjamin@mergington.edu", "role": "student"},
        {"email": "charlotte@mergington.edu", "role": "student"},
        {"email": "henry@mergington.edu", "role": "student"}
    ]

    # Activity-participant relationships
    relationships = {
        "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
        "Programming Class": ["emma@mergington.edu", "sophia@mergington.edu"],
        "Gym Class": ["john@mergington.edu", "olivia@mergington.edu"],
        "Soccer Team": ["liam@mergington.edu", "noah@mergington.edu"],
        "Basketball Team": ["ava@mergington.edu", "mia@mergington.edu"],
        "Art Club": ["amelia@mergington.edu", "harper@mergington.edu"],
        "Drama Club": ["ella@mergington.edu", "scarlett@mergington.edu"],
        "Math Club": ["james@mergington.edu", "benjamin@mergington.edu"],
        "Debate Team": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }

    connection = op.get_bind()

    # Insert users
    now = datetime.utcnow()
    for user in users:
        connection.execute(
            sa.text(
                'INSERT INTO users (email, role, created_at, updated_at) '
                'VALUES (:email, :role, :created_at, :updated_at)'
            ),
            {
                "email": user["email"],
                "role": user["role"],
                "created_at": now,
                "updated_at": now
            }
        )

    # Insert activities
    for activity in activities:
        connection.execute(
            sa.text(
                'INSERT INTO activities (name, description, schedule, max_participants, created_at, updated_at) '
                'VALUES (:name, :description, :schedule, :max_participants, :created_at, :updated_at)'
            ),
            {
                "name": activity["name"],
                "description": activity["description"],
                "schedule": activity["schedule"],
                "max_participants": activity["max_participants"],
                "created_at": now,
                "updated_at": now
            }
        )

    # Insert activity-participant relationships
    for activity_name, emails in relationships.items():
        activity_result = connection.execute(
            sa.text('SELECT id FROM activities WHERE name = :name'),
            {"name": activity_name}
        ).fetchone()
        
        if activity_result:
            activity_id = activity_result[0]
            for email in emails:
                user_result = connection.execute(
                    sa.text('SELECT id FROM users WHERE email = :email'),
                    {"email": email}
                ).fetchone()
                
                if user_result:
                    user_id = user_result[0]
                    connection.execute(
                        sa.text(
                            'INSERT INTO activity_participants (activity_id, user_id) '
                            'VALUES (:activity_id, :user_id)'
                        ),
                        {
                            "activity_id": activity_id,
                            "user_id": user_id
                        }
                    )

def downgrade():
    connection = op.get_bind()
    connection.execute(sa.text('DELETE FROM activity_participants'))
    connection.execute(sa.text('DELETE FROM activities'))
    connection.execute(sa.text('DELETE FROM users'))