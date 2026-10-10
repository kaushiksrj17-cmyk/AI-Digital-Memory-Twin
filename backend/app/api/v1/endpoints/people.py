"""People API Endpoints."""

from fastapi import APIRouter
from typing import List
from models.person import Person

router = APIRouter()


@router.get("/", response_model=List[Person])
async def list_people():
    """Retrieve individuals connected to the memorialized subject."""
    return [
        Person(
            id="demo-person-001",
            memorial_profile_id="demo-profile-001",
            full_name="Eleanor Vance",
            relationship_to_subject="Daughter",
            biographical_note="Primary memorial archive custodian and trustee."
        ),
        Person(
            id="demo-person-002",
            memorial_profile_id="demo-profile-001",
            full_name="Arthur Vance",
            relationship_to_subject="Spouse",
            biographical_note="Married 1970 in Oxford; preserved collaborative travel journals."
        ),
        Person(
            id="demo-person-003",
            memorial_profile_id="demo-profile-001",
            full_name="Prof. Harold Davies",
            relationship_to_subject="Mentor",
            biographical_note="Academic supervisor at Trinity College, Cambridge."
        )
    ]
