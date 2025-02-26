from sqlalchemy.ext.asyncio import AsyncSession
from models import Project, Education, Experience, Skill, Certification, Candidate
from sqlalchemy import select
from schema.projects import ProjectCreate
from schema.education import EducationCreate
from schema.experience import ExperienceCreate
from schema.skills import SkillCreate
from schema.certificates import CertificationCreate

async def create_project(db_session: AsyncSession, project_data: ProjectCreate) -> Project:
    new_project = Project(**project_data.model_dump())
    db_session.add(new_project)
    await db_session.commit()
    await db_session.refresh(new_project)
    return new_project

async def create_education(db_session: AsyncSession, education_data: EducationCreate) -> Education:
    new_education = Education(**education_data.model_dump())
    db_session.add(new_education)
    await db_session.commit()
    await db_session.refresh(new_education)
    return new_education

async def create_experience(db_session: AsyncSession, experience_data: ExperienceCreate) -> Experience:
    new_experience = Experience(**experience_data.model_dump())
    db_session.add(new_experience)
    await db_session.commit()
    await db_session.refresh(new_experience)
    return new_experience


async def create_skill(db_session: AsyncSession, skill_data:SkillCreate, candidate_id: int):
    # Check if the skill already exists
    result = await db_session.execute(select(Skill).where(Skill.name == skill_data.name))
    existing_skill = result.scalars().first()

    if existing_skill:
        # If the skill exists, associate it with the candidate
        candidate = await db_session.get(Candidate, candidate_id)
        if candidate and existing_skill not in candidate.skills:
            candidate.skills.append(existing_skill)
            await db_session.commit()
        return existing_skill
    else:
        # If the skill does not exist, create it and associate it with the candidate
        new_skill = Skill(**skill_data.model_dump())
        db_session.add(new_skill)
        await db_session.commit()
        await db_session.refresh(new_skill)

        # Associate the new skill with the candidate
        candidate = await db_session.get(Candidate, candidate_id)
        if candidate:
            candidate.skills.append(new_skill)
            await db_session.commit()

        return new_skill
async def create_certification(db_session: AsyncSession, certification_data: CertificationCreate) -> Certification:
    new_certification = Certification(**certification_data.model_dump())
    db_session.add(new_certification)
    await db_session.commit()
    await db_session.refresh(new_certification)
    return new_certification

