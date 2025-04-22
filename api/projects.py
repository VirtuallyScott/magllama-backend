from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timezone

from .main import get_db
from .security import check_permission, check_project_access, log_activity

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
async def create_project(project: Project, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    await check_permission(user_id, "create_project", db)
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO projects (name, parent_id, description) VALUES ($1, $2, $3) RETURNING id, name, parent_id, description",
            project.name, project.parent_id, project.description
        )
        await log_activity(user_id, "create_project", {"project": project.dict()}, db)
        return dict(row)

@router.get("/projects", response_model=List[Project])
async def list_projects(include_inactive: bool = False, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    await check_permission(user_id, "list_projects", db)
    query = "SELECT id, name, parent_id, description FROM projects"
    if not include_inactive:
        query += " WHERE inactive_at IS NULL"
    async with db.acquire() as conn:
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]

@router.delete("/projects/{project_id}")
async def deactivate_project(project_id: uuid.UUID, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    await check_permission(user_id, "deactivate_project", db)
    now = datetime.now(timezone.utc)
    async with db.acquire() as conn:
        # Verify user has access to the project before deactivating
        await check_project_access(user_id, project_id, db)
        await conn.execute(
            "UPDATE projects SET inactive_at = $1, inactivated_by = $2 WHERE id = $3",
            now, user_id, project_id
        )
        await log_activity(user_id, "deactivate_project", {"project_id": str(project_id)}, db)
    return {"detail": "Project marked as inactive"}

@router.post("/project_members", response_model=ProjectMember)
async def add_project_member(member: ProjectMember, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    await check_permission(user_id, "assign_project_role", db)
    # Verify user has access to the project before adding members
    await check_project_access(user_id, member.project_id, db)
    async with db.acquire() as conn:
        await conn.execute(
            "INSERT INTO project_members (project_id, user_id, role_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            member.project_id, member.user_id, member.role_id
        )
        await log_activity(user_id, "add_project_member", {"member": member.dict()}, db)
        return member

@router.get("/project_members/{project_id}", response_model=List[ProjectMember])
async def get_project_members(project_id: uuid.UUID, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    await check_project_access(user_id, project_id, db)
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT project_id, user_id, role_id FROM project_members WHERE project_id = $1",
            project_id
        )
        return [ProjectMember(project_id=row['project_id'], user_id=row['user_id'], role_id=row['role_id']) for row in rows]
