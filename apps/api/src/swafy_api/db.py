from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from swafy_api.config import get_settings, normalize_database_url


class Base(DeclarativeBase):
    pass


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        normalize_database_url(get_settings().database_url),
        pool_pre_ping=True,
        future=True,
    )
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
