# tests/conftest.py
from typing import AsyncGenerator

import httpx
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.schema import DefaultClause
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from app.core.database import Base  # ← your declarative base
from app.main import app as fastapi_app
from app.core.deps import get_db  # ← dependency that returns AsyncSession

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ── create a fresh in-memory DB for every *test function* ───────────────────
@pytest_asyncio.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DB_URL, echo=False)

    for table in Base.metadata.sorted_tables:
        for col in table.columns:
            default = col.server_default
            if default is None:
                continue

            default_sql = str(
                default.arg  # type: ignore[attr-defined]
                if isinstance(default.arg, (str, TextClause))  # type: ignore[attr-defined]
                else default.arg.compile(compile_kwargs={"literal_binds": True})  # type: ignore[attr-defined]
            )

            if "date_trunc" in default_sql.lower():
                col.server_default = DefaultClause(text("CURRENT_TIMESTAMP"))

    # Build tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Yield a session bound to this engine
    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with SessionLocal() as session:
        yield session

    await engine.dispose()


# ── override FastAPI dependency so endpoints use the *same* session ─────────
@pytest_asyncio.fixture(autouse=True)
def _override_get_db(async_session):
    fastapi_app.dependency_overrides[get_db] = lambda: async_session
    yield
    fastapi_app.dependency_overrides.clear()


# ── lightweight async client for hitting endpoints ──────────────────────────
@pytest_asyncio.fixture()
async def client():
    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
