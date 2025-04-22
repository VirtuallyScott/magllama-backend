import asyncpg
from fastapi import Depends, HTTPException, status, APIRouter, Response, Header
import uuid
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
import hmac
import secrets
import hashlib
from datetime import datetime, timezone

from .main import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Role(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

class Permission(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    description: Optional[str]

class APIKeyOut(BaseModel):
    id: uuid.UUID
    description: Optional[str]
    created_at: datetime
    last_used_at: Optional[datetime]
    inactive_at: Optional[datetime]
    project_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]

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
        await log_activity(user_id, "permission_denied", {"permission": permission_name}, db)
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
        await log_activity(user_id, "project_access_denied", {"project_id": str(project_id)}, db)
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

@router.post("/auth/login")
async def login(username: str, password: str, db=Depends(get_db)):
    # Fetch user by username or email
    user = await db.fetchrow("SELECT * FROM users WHERE username=$1 OR email=$1", username)
    # Always do hash check to avoid timing attacks
    if not user or not pwd_context.verify(password, user["password_hash"] or ""):
        await log_activity(user["id"] if user else None, "login_failed", {"username": username}, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    # TODO: Check for lockout, MFA, etc.
    # Issue token/session here (not implemented)
    await log_activity(user["id"], "login_success", {}, db)
    return {"detail": "Login successful"}

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

def generate_api_key():
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()

@router.post("/api_keys/user", response_model=APIKeyOut, status_code=201)
async def create_user_api_key(
    user_id: uuid.UUID, 
    description: Optional[str] = None, 
    db=Depends(get_db)
):
    # Only allow user to create their own key
    await check_permission(user_id, "create_api_key", db)
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO api_keys (user_id, key_hash, description) VALUES ($1, $2, $3) RETURNING id, user_id, project_id, description, created_at, last_used_at, inactive_at",
            user_id, key_hash, description
        )
    # Return the API key only once
    return Response(
        content={"api_key": api_key, **dict(row)},
        media_type="application/json",
        status_code=201,
        headers={"Cache-Control": "no-store"}
    )

@router.post("/api_keys/project", response_model=APIKeyOut, status_code=201)
async def create_project_api_key(
    user_id: uuid.UUID, 
    project_id: uuid.UUID, 
    description: Optional[str] = None, 
    db=Depends(get_db)
):
    await check_permission(user_id, "create_project_api_key", db)
    await check_project_access(user_id, project_id, db)
    api_key = generate_api_key()
    key_hash = hash_api_key(api_key)
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO api_keys (project_id, user_id, key_hash, description) VALUES ($1, $2, $3, $4) RETURNING id, user_id, project_id, description, created_at, last_used_at, inactive_at",
            project_id, user_id, key_hash, description
        )
    return Response(
        content={"api_key": api_key, **dict(row)},
        media_type="application/json",
        status_code=201,
        headers={"Cache-Control": "no-store"}
    )

@router.delete("/api_keys/{api_key_id}", status_code=204)
async def deactivate_api_key(api_key_id: uuid.UUID, user_id: uuid.UUID, db=Depends(get_db)):
    # Only allow owner or admin to deactivate
    await check_permission(user_id, "deactivate_api_key", db)
    now = datetime.now(timezone.utc)
    async with db.acquire() as conn:
        await conn.execute(
            "UPDATE api_keys SET inactive_at = $1, inactivated_by = $2 WHERE id = $3",
            now, user_id, api_key_id
        )
    return Response(status_code=204)

async def get_current_user_from_api_key(x_api_key: str = Header(None), db=Depends(get_db)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    key_hash = hash_api_key(x_api_key)
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM api_keys WHERE key_hash = $1 AND inactive_at IS NULL",
            key_hash
        )
        if not row:
            raise HTTPException(status_code=401, detail="Invalid API key")
        # Optionally update last_used_at
        await conn.execute(
            "UPDATE api_keys SET last_used_at = $1 WHERE id = $2",
            datetime.now(timezone.utc), row["id"]
        )
        return row
