from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid

from .main import get_db

router = APIRouter()

class Project(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    parent_id: Optional[uuid.UUID]
    description: Optional[str]

class ProjectMember(BaseModel):
    project_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID

@router.post("/projects", response_model=Project)
async def create_project(project: Project, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO projects (name, parent_id, description) VALUES ($1, $2, $3) RETURNING id, name, parent_id, description",
            project.name, project.parent_id, project.description
        )
        return dict(row)

@router.get("/projects", response_model=List[Project])
async def list_projects(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, parent_id, description FROM projects")
        return [dict(row) for row in rows]

@router.post("/project_members", response_model=ProjectMember)
async def add_project_member(member: ProjectMember, db=Depends(get_db)):
    async with db.acquire() as conn:
        await conn.execute(
            "INSERT INTO project_members (project_id, user_id, role_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            member.project_id, member.user_id, member.role_id
        )
        return member

@router.get("/project_members/{project_id}", response_model=List[ProjectMember])
async def get_project_members(project_id: uuid.UUID, db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT project_id, user_id, role_id FROM project_members WHERE project_id = $1",
            project_id
        )
        return [ProjectMember(project_id=row['project_id'], user_id=row['user_id'], role_id=row['role_id']) for row in rows]
