import structlog
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi_limiter.depends import RateLimiter
from api.deps import DBSessionDep
from schema.candidates import CandidateCreate, CandidateUpdate, CandidateResponse
from schema.responses import ResponseBase, create_response
from crud.candidates import (
    create_candidate,
    get_candidate,
    update_candidate,
    get_candidate_by_email,
)

router = APIRouter()
logger = structlog.stdlib.get_logger()

# create candidate
@router.post(
    "/",
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
    return create_response(candidate , message="Candidate created successfully")

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

# update candidate
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
