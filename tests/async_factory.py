from factory.alchemy import SQLAlchemyModelFactory
from sqlalchemy.ext.asyncio import AsyncSession


class AsyncFactory(SQLAlchemyModelFactory):
    """Minimal async helper for SQLAlchemy models."""

    class Meta:  # noqa: D106
        abstract = True
        sqlalchemy_session_persistence = "flush"  # flush, don’t commit

    @classmethod
    async def create_async(cls, session: AsyncSession, **kwargs):
        """Async drop-in for .create().  Always pass a session."""
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.flush()  # PKs populated
        return obj
