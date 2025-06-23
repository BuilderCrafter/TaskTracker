from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.deps import get_db

router = APIRouter(tags=["meta"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    # quick “SELECT 1” round-trip
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
