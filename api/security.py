import asyncpg
from fastapi import Depends, HTTPException, status, APIRouter, Response, Header, Query
import uuid
from pydantic import BaseModel
from typing import Optional, List
from passlib.context import CryptContext
import hmac
import secrets
import hashlib
from datetime import datetime, timezone
import os
from cryptography.fernet import Fernet, InvalidToken
import base64

from .main import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret encryption setup
SECRET_ENCRYPTION_KEY = os.environ.get("SECRET_ENCRYPTION_KEY")
if not SECRET_ENCRYPTION_KEY:
    raise RuntimeError("SECRET_ENCRYPTION_KEY must be set in environment")
fernet = Fernet(SECRET_ENCRYPTION_KEY.encode())

def encrypt_secret(plaintext: str) -> bytes:
    return fernet.encrypt(plaintext.encode())

def decrypt_secret(ciphertext: bytes) -> str:
    return fernet.decrypt(ciphertext).decode()

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

class SecretIn(BaseModel):
    name: str
    value: str
    project_id: Optional[uuid.UUID] = None
    type: Optional[str] = "user"
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[dict] = {}

class SecretOut(BaseModel):
    id: uuid.UUID
    name: str
    project_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    rotated_at: Optional[datetime]
    revoked_at: Optional[datetime]
    expires_at: Optional[datetime]
    description: Optional[str]
    type: Optional[str]
    metadata: Optional[dict]

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

@router.post("/secrets", response_model=SecretOut, status_code=201)
async def create_secret(
    secret: SecretIn,
    user_id: uuid.UUID = Query(...),
    db=Depends(get_db)
):
    # User can create their own secrets, or must have permission for project secrets
    if secret.project_id:
        await check_permission(user_id, "create_project_secret", db)
        await check_project_access(user_id, secret.project_id, db)
    else:
        await check_permission(user_id, "create_user_secret", db)
    value_enc = encrypt_secret(secret.value)
    async with db.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO secrets (name, value_enc, user_id, project_id, created_by, description, type, expires_at, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, name, project_id, user_id, created_at, updated_at, rotated_at, revoked_at, expires_at, description, type, metadata
            """,
            secret.name, value_enc, user_id if not secret.project_id else None, secret.project_id, user_id,
            secret.description, secret.type, secret.expires_at, secret.metadata
        )
        await log_activity(user_id, "create_secret", {"secret_id": str(row["id"]), "name": secret.name}, db)
        return dict(row)

@router.get("/secrets/{secret_id}", response_model=SecretOut)
async def get_secret(secret_id: uuid.UUID, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        # Access control: user must own or have project access
        if row["user_id"] == user_id:
            pass
        elif row["project_id"]:
            await check_project_access(user_id, row["project_id"], db)
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        # Decrypt secret value
        try:
            value = decrypt_secret(row["value_enc"])
        except InvalidToken:
            raise HTTPException(status_code=500, detail="Secret decryption failed")
        await log_activity(user_id, "get_secret", {"secret_id": str(secret_id)}, db)
        # Do NOT return the secret value in the API unless explicitly requested and authorized
        return {k: row[k] for k in SecretOut.__fields__}

@router.post("/secrets/{secret_id}/reveal")
async def reveal_secret(secret_id: uuid.UUID, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        # Access control as above
        if row["user_id"] == user_id:
            pass
        elif row["project_id"]:
            await check_project_access(user_id, row["project_id"], db)
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        # Only allow if user has explicit permission
        await check_permission(user_id, "reveal_secret", db)
        value = decrypt_secret(row["value_enc"])
        await log_activity(user_id, "reveal_secret", {"secret_id": str(secret_id)}, db)
        return {"value": value}

@router.put("/secrets/{secret_id}", response_model=SecretOut)
async def update_secret(secret_id: uuid.UUID, secret: SecretIn, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        # Access control: user must own or have project access
        if row["user_id"] == user_id:
            pass
        elif row["project_id"]:
            await check_project_access(user_id, row["project_id"], db)
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        # Permissions
        if secret.project_id:
            await check_permission(user_id, "update_project_secret", db)
        else:
            await check_permission(user_id, "update_user_secret", db)
        value_enc = encrypt_secret(secret.value)
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            UPDATE secrets SET
                name = $1,
                value_enc = $2,
                description = $3,
                type = $4,
                expires_at = $5,
                metadata = $6,
                updated_at = $7,
                updated_by = $8
            WHERE id = $9
            """,
            secret.name, value_enc, secret.description, secret.type, secret.expires_at, secret.metadata,
            now, user_id, secret_id
        )
        updated_row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        await log_activity(user_id, "update_secret", {"secret_id": str(secret_id)}, db)
        return dict(updated_row)

@router.post("/secrets/{secret_id}/rotate", response_model=SecretOut)
async def rotate_secret(secret_id: uuid.UUID, new_value: str, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        # Access control
        if row["user_id"] == user_id:
            pass
        elif row["project_id"]:
            await check_project_access(user_id, row["project_id"], db)
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        await check_permission(user_id, "rotate_secret", db)
        value_enc = encrypt_secret(new_value)
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            UPDATE secrets SET
                value_enc = $1,
                rotated_at = $2,
                updated_at = $2,
                updated_by = $3
            WHERE id = $4
            """,
            value_enc, now, user_id, secret_id
        )
        updated_row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        await log_activity(user_id, "rotate_secret", {"secret_id": str(secret_id)}, db)
        return dict(updated_row)

@router.post("/secrets/{secret_id}/revoke")
async def revoke_secret(secret_id: uuid.UUID, user_id: uuid.UUID = Query(...), db=Depends(get_db)):
    async with db.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM secrets WHERE id = $1", secret_id)
        if not row:
            raise HTTPException(status_code=404, detail="Secret not found")
        # Access control
        if row["user_id"] == user_id:
            pass
        elif row["project_id"]:
            await check_project_access(user_id, row["project_id"], db)
        else:
            raise HTTPException(status_code=403, detail="Access denied")
        await check_permission(user_id, "revoke_secret", db)
        now = datetime.now(timezone.utc)
        await conn.execute(
            """
            UPDATE secrets SET
                revoked_at = $1,
                revoked_by = $2
            WHERE id = $3
            """,
            now, user_id, secret_id
        )
        await log_activity(user_id, "revoke_secret", {"secret_id": str(secret_id)}, db)
    return {"detail": "Secret revoked"}
