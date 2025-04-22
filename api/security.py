import asyncpg
from fastapi import Depends, HTTPException, status, APIRouter
import uuid
from pydantic import BaseModel
from typing import Optional, List

from .main import get_db

router = APIRouter()

class Role(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

class Permission(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

@router.post("/roles", response_model=Role)
async def create_role(role: Role, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO roles (name, description) VALUES ($1, $2) RETURNING id, name, description",
            role.name, role.description
        )
        return dict(row)

@router.get("/roles", response_model=List[Role])
async def list_roles(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, description FROM roles")
        return [dict(row) for row in rows]

@router.post("/permissions", response_model=Permission)
async def create_permission(permission: Permission, db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO permissions (name, description) VALUES ($1, $2) RETURNING id, name, description",
            permission.name, permission.description
        )
        return dict(row)

@router.get("/permissions", response_model=List[Permission])
async def list_permissions(db=Depends(get_db)):
    async with db.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, description FROM permissions")
        return [dict(row) for row in rows]

@router.get("/check_permission/{user_id}/{permission_name}")
async def check_permission_endpoint(user_id: uuid.UUID, permission_name: str, db=Depends(get_db)):
    await check_permission(user_id, permission_name, db)
    return {"detail": "Permission granted"}

async def check_permission(user_id: uuid.UUID, permission_name: str, db):
    query = """
        SELECT 1 FROM user_roles ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        WHERE ur.user_id = $1 AND p.name = $2
        LIMIT 1
    """
    result = await db.fetchrow(query, user_id, permission_name)
    if not result:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

async def check_project_access(user_id: uuid.UUID, project_id: uuid.UUID, db, required_role: str = None):
    query = """
        SELECT 1 FROM project_members pm
        JOIN roles r ON pm.role_id = r.id
        WHERE pm.user_id = $1 AND pm.project_id = $2
        {role_clause}
        LIMIT 1
    """
    role_clause = ""
    params = [user_id, project_id]
    if required_role:
        role_clause = "AND r.name = $3"
        params.append(required_role)
    result = await db.fetchrow(query.format(role_clause=role_clause), *params)
    if not result:
        raise HTTPException(status_code=403, detail="Access denied for this project")

@router.post("/log_activity")
async def log_activity_endpoint(user_id: uuid.UUID, action: str, details: dict = None, db=Depends(get_db)):
    await log_activity(user_id, action, details, db)
    return {"detail": "Activity logged"}

async def log_activity(user_id: uuid.UUID, action: str, details: dict, db):
    await db.execute(
        "INSERT INTO activity_logs (user_id, action, details) VALUES ($1, $2, $3)",
        user_id, action, details
    )

# Placeholder for OAuth2 login
@router.post("/auth/oauth2")
async def oauth2_login(token: str, db=Depends(get_db)):
    # TODO: Validate token with OAuth2 provider, extract user info
    # If user exists in DB, return user; else, create user with external_id/idp_provider
    pass

# Placeholder for LDAP login
@router.post("/auth/ldap")
async def ldap_login(username: str, password: str, db=Depends(get_db)):
    # TODO: Authenticate against LDAP, extract user info
    # If user exists in DB, return user; else, create user with external_id/idp_provider
    pass

# Placeholder for SAML login
@router.post("/auth/saml")
async def saml_login(saml_response: str, db=Depends(get_db)):
    # TODO: Parse SAML response, extract user info
    # If user exists in DB, return user; else, create user with external_id/idp_provider
    pass
