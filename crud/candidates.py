from typing import List
from models import Candidate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query
from schema.candidates import CandidateCreate, CandidateUpdate
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import IntegrityError

async def get_candidates_paginated(
    db_session: AsyncSession,
    page: int = 1,
    size: int = 10,
) -> List[Candidate]:
    query = select(Candidate).options(
        selectinload(Candidate.certifications),
        selectinload(Candidate.educations),
        selectinload(Candidate.experiences),
        selectinload(Candidate.projects),
        selectinload(Candidate.skills),
    ) 
    query = query.limit(size).offset((page - 1) * size)
    result = await db_session.execute(query)
    candidates = result.scalars().all() 
    return candidates

async def get_candidates_count(db_session: AsyncSession) -> int:
    result = await db_session.execute(select(func.count()).select_from(Candidate))
    return result.scalar()

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
    db_session: AsyncSession, candidate: CandidateCreate, emmbeddings_namespace: str | None = None
) -> Candidate:
    candidate = Candidate(**candidate.model_dump())
    if emmbeddings_namespace:
        candidate.embeddings_namespace = emmbeddings_namespace
    db_session.add(candidate)
    try:
        await db_session.commit()
    except IntegrityError as e:
        await db_session.rollback()
        raise e

    # Reload the candidate with all necessary relationships
    query = (
        select(Candidate)
        .options(
            selectinload(Candidate.educations),
            selectinload(Candidate.experiences),
            selectinload(Candidate.projects),
            selectinload(Candidate.certifications),
            selectinload(Candidate.skills),
        )
        .where(Candidate.id == candidate.id)
    )
    result = await db_session.execute(query)
    candidate = result.scalars().first()
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
