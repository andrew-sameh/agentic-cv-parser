from models import Candidate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from schema.candidates import CandidateCreate, CandidateUpdate
from fastapi_pagination.ext.asyncpg import paginate
from fastapi_pagination import Params, Page


async def get_candidates_paginated(
    db_session: AsyncSession,
    params: Params | None = Params(),
) -> Page[Candidate]:
    query = select(Candidate).options(
        selectinload(Candidate.certifications),
        selectinload(Candidate.educations),
        selectinload(Candidate.experiences),
        selectinload(Candidate.projects),
        selectinload(Candidate.skills),
    )
    output = await paginate(db_session, query, params)
    return output


async def get_candidate(db_session: AsyncSession, candidate_id: int) -> Candidate:
    candidate = (
        await db_session.scalars(
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.certifications),
                selectinload(Candidate.educations),
                selectinload(Candidate.experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.skills),
            )
        )
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


async def get_candidate_by_email(db_session: AsyncSession, email: str) -> Candidate:
    return (
        await db_session.scalars(
            select(Candidate)
            .where(Candidate.email == email)
            .options(
                selectinload(Candidate.certifications),
                selectinload(Candidate.educations),
                selectinload(Candidate.experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.skills),
            )
        )
    ).first()


async def get_candidate_by_embeddings_namespace(
    db_session: AsyncSession, embeddings_namespace: str
) -> Candidate:
    return (
        await db_session.scalars(
            select(Candidate)
            .where(Candidate.embeddings_namespace == embeddings_namespace)
            .options(
                selectinload(Candidate.certifications),
                selectinload(Candidate.educations),
                selectinload(Candidate.experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.skills),
            )
        )
    ).first()


async def create_candidate(
    db_session: AsyncSession, candidate: CandidateCreate
) -> Candidate:
    candidate = Candidate(**candidate.model_dump())
    db_session.add(candidate)
    await db_session.commit()
    return candidate


async def update_candidate(
    db_session: AsyncSession, candidate_id: int, candidate_in: CandidateUpdate
) -> Candidate:
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
