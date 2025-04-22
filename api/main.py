
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import os
import uuid

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/postgres")

@app.on_event("startup")
async def startup():
    app.state.db = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.db.close()

@app.get("/")
async def root():
    return {"message": "magllama API is running"}


# Pydantic models

class Role(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

class Permission(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

class UserRole(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID

class ActivityLog(BaseModel):
    id: Optional[uuid.UUID]
    user_id: uuid.UUID
    action: str
    details: Optional[dict]
    timestamp: Optional[str]

class Project(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    parent_id: Optional[uuid.UUID]
    description: Optional[str]

class ProjectMember(BaseModel):
    project_id: uuid.UUID
    user_id: uuid.UUID
    role_id: uuid.UUID


# Dependency to get DB connection
async def get_db():
    return app.state.db


# Permission check dependency example (stub)
async def check_permission(permission_name: str, db=Depends(get_db)):
    # This is a placeholder for permission checking logic.
    # In real implementation, extract user info from auth token,
    # query user roles and permissions, and verify permission_name.
    # Raise HTTPException if permission denied.
    # For now, allow all.
    pass


# Role endpoints

@app.post("/roles", response_model=Role)
async def create_role(role: Role, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO roles (name, description) VALUES ($1, $2) RETURNING id, name, description",
            role.name, role.description
        )
        return dict(row)

@app.get("/roles", response_model=List[Role])
async def list_roles(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, description FROM roles")
        return [dict(row) for row in rows]

# Permission endpoints

@app.post("/permissions", response_model=Permission)
async def create_permission(permission: Permission, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO permissions (name, description) VALUES ($1, $2) RETURNING id, name, description",
            permission.name, permission.description
        )
        return dict(row)

@app.get("/permissions", response_model=List[Permission])
async def list_permissions(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, description FROM permissions")
        return [dict(row) for row in rows]

# User-Role assignment endpoints

@app.post("/user_roles", response_model=UserRole)
async def assign_role(user_role: UserRole, db=Depends(get_db)):
    async with db.acquire() as conn:
        await conn.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_role.user_id, user_role.role_id
        )
        return user_role

@app.get("/user_roles/{user_id}", response_model=List[UserRole])
async def get_user_roles(user_id: uuid.UUID, db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id, role_id FROM user_roles WHERE user_id = $1",
            user_id
        )
        return [UserRole(user_id=row['user_id'], role_id=row['role_id']) for row in rows]

# Activity log endpoint (read-only)

@app.get("/activity_logs", response_model=List[ActivityLog])
async def list_activity_logs(limit: int = 100, db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, user_id, action, details, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT $1",
            limit
        )
        return [dict(row) for row in rows]

# Project endpoints

@app.post("/projects", response_model=Project)
async def create_project(project: Project, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO projects (name, parent_id, description) VALUES ($1, $2, $3) RETURNING id, name, parent_id, description",
            project.name, project.parent_id, project.description
        )
        return dict(row)

@app.get("/projects", response_model=List[Project])
async def list_projects(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, parent_id, description FROM projects")
        return [dict(row) for row in rows]

# Project membership endpoints

@app.post("/project_members", response_model=ProjectMember)
async def add_project_member(member: ProjectMember, db=Depends(get_db)):
    async with db.acquire() as conn:
        await conn.execute(
            "INSERT INTO project_members (project_id, user_id, role_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            member.project_id, member.user_id, member.role_id
        )
        return member

@app.get("/project_members/{project_id}", response_model=List[ProjectMember])
async def get_project_members(project_id: uuid.UUID, db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch(
            "SELECT project_id, user_id, role_id FROM project_members WHERE project_id = $1",
            project_id
        )
        return [ProjectMember(project_id=row['project_id'], user_id=row['user_id'], role_id=row['role_id']) for row in rows]

# Example of activity logging helper function

async def log_activity(user_id: uuid.UUID, action: str, details: Optional[dict], db):
    async with db.acquire() as conn:
        await conn.execute(
            "INSERT INTO activity_logs (user_id, action, details) VALUES ($1, $2, $3)",
            user_id, action, details
        )
