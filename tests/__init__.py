from factory.base import Factory

Factory._meta.sqlalchemy_session_persistence = "flush"  # type: ignore[attr-defined]
