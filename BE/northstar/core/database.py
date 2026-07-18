import json
import sqlite3
from collections.abc import Generator
from datetime import datetime
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from northstar.core.config import get_settings

sqlite3.register_adapter(datetime, lambda value: value.isoformat())


def _connect_args(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"check_same_thread": False, "timeout": 30}
    return {}


settings = get_settings()
engine: Engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@event.listens_for(engine, "connect")
def configure_sqlite(connection: object, _record: object) -> None:
    if not settings.database_url.startswith("sqlite"):
        return
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


def get_db() -> Generator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def initialize_database() -> None:
    migrations = Path(__file__).resolve().parents[2] / "migrations"
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE IF NOT EXISTS python_migrations "
            "(name VARCHAR(255) PRIMARY KEY, applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        applied = {
            row[0]
            for row in connection.exec_driver_sql("SELECT name FROM python_migrations").fetchall()
        }
        for migration in sorted(migrations.glob("*.sql")):
            if migration.name in applied:
                continue
            raw = migration.read_text(encoding="utf-8")
            for statement in raw.split("-- statement"):
                sql = statement.strip()
                if sql:
                    connection.exec_driver_sql(sql)
            connection.exec_driver_sql(
                "INSERT INTO python_migrations (name) VALUES (?)",
                (migration.name,),
            )


def json_value(value: object, fallback: object) -> object:
    if value is None:
        return fallback
    if isinstance(value, dict | list):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback
