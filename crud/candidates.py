from models import Candidates
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schema.candidates import CandidateCreate, CandidateUpdate


async def get_candidate(db_session: AsyncSession, candidate_id: int) -> Candidates:
    candidate = (await db_session.scalars(select(Candidates).where(Candidates.id == candidate_id))).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidates not found")
    return candidate 


async def get_candidate_by_email(db_session: AsyncSession, email: str) -> Candidates:
    return (await db_session.scalars(select(Candidates).where(Candidates.email == email))).first()

async def create_candidate(db_session: AsyncSession, candidate: CandidateCreate) -> Candidates:
    candidate = Candidates(**candidate.model_dump())
    db_session.add(candidate)
    await db_session.commit()
    return candidate


async def update_candidate(db_session: AsyncSession, candidate_id: int, candidate_in: CandidateUpdate) -> Candidates:
    candidate = await get_candidate(db_session, candidate_id)
    if isinstance(candidate_in, dict):
        update_data = candidate_in 
    else:
        update_data = candidate_in.model_dump(
            exclude_unset=True
        )  # this tells pydantic to not include the values that were not sent
    for field in update_data:
        setattr(candidate, field, update_data[field])

    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)
    return candidate 
