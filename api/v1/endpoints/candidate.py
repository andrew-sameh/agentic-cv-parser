import os
import structlog
from fastapi import APIRouter, Depends, Request, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from api.deps import DBSessionDep
from schema.candidates import CandidateCreate, CandidateUpdate, CandidateResponse
from schema.certificates import CertificationCreate 
from schema.education import EducationCreate 
from schema.experience import ExperienceCreate 
from schema.skills import SkillCreate 
from schema.projects import ProjectCreate 
from schema.responses import ResponseBase, ResponseBasePaginated, create_response, create_paginated_response
from crud.candidates import (
    create_candidate,
    get_candidate,
    update_candidate,
    get_candidate_by_email,
    get_candidates_paginated,
    get_candidate_by_embeddings_namespace,
    get_candidates_count,
)
from crud.sections import (
    create_certification,
    create_education,
    create_experience,
    create_skill,
    create_project,
)
from services.documents import document_processor

router = APIRouter()
logger = structlog.stdlib.get_logger()

# upload a candidate's resume
@router.post(
    "/",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[CandidateResponse],
    status_code=201,
)
async def upload_candidate_resume(
    request: Request,
    db_session: DBSessionDep,
    file: UploadFile = File(...),
):
    allowed_extensions = [".pdf", ".docx" ]

    file_name = file.filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    namespace = os.urandom(10).hex()
    await logger.info(f"Uploading file {file_name} with extension {file_extension}")
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}",
        )
    
    candidate, certs, edu, exp, skills, projects, content = await document_processor.process_file_upload(file, namespace)

    # Create candidate in the database
    candidate = await create_candidate(db_session, CandidateCreate(**candidate.model_dump(),embeddings_namespace=namespace,status='active',content=content))
    await logger.info("Candidate created", candidate_id=candidate.id)

    # Add certifications
    for cert in certs.certifications:
        cert_in = CertificationCreate(**cert.model_dump(), candidate_id=candidate.id)
        await create_certification(db_session, cert_in)
    # Add educations
    for education in edu.education_entries:
        edu_in = EducationCreate(**education.model_dump(), candidate_id=candidate.id)
        await create_education(db_session, edu_in)
    # Add experiences
    for experience in exp.experiences:
        exp_in = ExperienceCreate(**experience.model_dump(), candidate_id=candidate.id)
        await create_experience(db_session, exp_in)

    # Add projects
    for project in projects.projects:
        project_in = ProjectCreate(**project.model_dump(), candidate_id=candidate.id)
        await create_project(db_session, project_in)

    # Add skills
    for skill in skills.skills:
        skill_in = SkillCreate(**skill.model_dump())
        await create_skill(db_session, skill_in, candidate.id)
    await logger.info("Candidate details created successfully", candidate_id=candidate.id)

    await db_session.refresh(candidate)
    updated_candidate = await get_candidate(db_session, candidate.id)
    return create_response(updated_candidate, message="Candidate created successfully") 



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
    page: int = 1,
    size: int = 10,
):
    await logger.info("Getting candidates paginated")
    total = await get_candidates_count(db_session)
    candidates = await get_candidates_paginated(db_session, page, size)
    return create_paginated_response(candidates, page, size, total)


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


# create candidate manually (Test)
# @router.post(
#     "/manual/",
#     dependencies=[Depends(RateLimiter(times=10, seconds=20))],
#     response_model=ResponseBase[CandidateResponse],
#     status_code=201,
# )
# async def create_candidate_ep(
#     candidate_in: CandidateCreate,
#     request: Request,
#     db_session: DBSessionDep,
# ):
#     if await get_candidate_by_email(db_session, candidate_in.email):
#         await logger.error("Candidate already exists", email=candidate_in.email)
#         raise HTTPException(status_code=400, detail="Candidate already exists")
#     if candidate_in.embeddings_namespace:
#         if await get_candidate_by_embeddings_namespace(
#             db_session, candidate_in.embeddings_namespace
#         ):
#             await logger.error(
#                 "Candidate embeddings namespace already exists",
#                 embeddings_namespace=candidate_in.embeddings_namespace,
#             )
#     await logger.info("Creating candidate", body=candidate_in)
#     candidate = await create_candidate(db_session, candidate_in)
#     await logger.info("Candidate created", candidate_id=candidate.id)
#     return create_response(candidate, message="Candidate created successfully")


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
