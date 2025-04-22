import asyncpg
from fastapi import Depends, HTTPException, status, APIRouter
import uuid

from .main import get_db

router = APIRouter()

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

@router.post("/log_activity")
async def log_activity_endpoint(user_id: uuid.UUID, action: str, details: dict = None, db=Depends(get_db)):
    await log_activity(user_id, action, details, db)
    return {"detail": "Activity logged"}

async def log_activity(user_id: uuid.UUID, action: str, details: dict, db):
    await db.execute(
        "INSERT INTO activity_logs (user_id, action, details) VALUES ($1, $2, $3)",
        user_id, action, details
    )
