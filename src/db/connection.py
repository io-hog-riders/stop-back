from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from db.models import Base
from env import DATABASE_URL

engine = create_engine(
	DATABASE_URL,
	echo=False,
	pool_pre_ping=True,
)

SessionLocal = sessionmaker(
	bind=engine,
	autocommit=False,
	autoflush=False,
	expire_on_commit=False,
)


def init_db() -> None:
	Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def ping_db(db: Session) -> None:
	db.execute(text("SELECT 1"))
