import structlog
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_limiter.depends import RateLimiter
from fastapi_pagination import Params
from api.deps import DBSessionDep
from schema.candidates import CandidateCreate, CandidateUpdate, CandidateResponse
from schema.responses import ResponseBase, ResponseBasePaginated, create_response
from crud.candidates import (
    create_candidate,
    get_candidate,
    update_candidate,
    get_candidate_by_email,
    get_candidates_paginated,
)

router = APIRouter()
logger = structlog.stdlib.get_logger()


# get candidates paginated
@router.get(
    "/",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBasePaginated[CandidateResponse],
    status_code=200,
)
async def get_candidates(
    request: Request,
    db_session: DBSessionDep,
    params: Params = Depends(),
):
    await logger.info("Getting candidates paginated")
    candidates = await get_candidates_paginated(db_session,params)
    return create_response(candidates)


# get candidate by id
@router.get(
    "/{candidate_id}",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[CandidateResponse],
    status_code=200,
)
async def get_candidate_by_id(
    candidate_id: int,
    request: Request,
    db_session: DBSessionDep,
):
    await logger.info("Getting candidate by id", candidate_id=candidate_id)
    candidate = await get_candidate(db_session, candidate_id)
    return create_response(candidate)


@router.put(
    "/{candidate_id}",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[CandidateResponse],
    status_code=200,
)
async def update_candidate_endpoint(
    candidate_id: int,
    candidate_in: CandidateUpdate,
    request: Request,
    db_session: DBSessionDep,
):
    await logger.info("Updating candidate", candidate_id=candidate_id)
    candidate = await update_candidate(db_session, candidate_id, candidate_in)
    return create_response(candidate, message="Candidate updated successfully")


# create candidate
@router.post(
    "/manual/",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[CandidateResponse],
    status_code=201,
)
async def create_candidate_ep(
    candidate_in: CandidateCreate,
    request: Request,
    db_session: DBSessionDep,
):
    if await get_candidate_by_email(db_session, candidate_in.email):
        await logger.error("Candidate already exists", email=candidate_in.email)
        raise HTTPException(status_code=400, detail="Candidate already exists")
    await logger.info("Creating candidate", body=candidate_in)
    candidate = await create_candidate(db_session, candidate_in)
    await logger.info("Candidate created", candidate_id=candidate.id)
    return create_response(candidate, message="Candidate created successfully")


# update candidate
# get candidate by email
@router.get(
    "/email/{email}",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[CandidateResponse],
    status_code=200,
)
async def get_candidate_by_email_endpoint(
    email: str,
    request: Request,
    db_session: DBSessionDep,
):
    await logger.info("Getting candidate by email", email=email)
    candidate = await get_candidate_by_email(db_session, email)
    return create_response(candidate)
