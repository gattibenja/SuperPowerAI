from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)


def _ensure_recordatorio_columns():
    if engine.dialect.name != "sqlite":
        return

    with engine.begin() as conn:
        columns = conn.exec_driver_sql("PRAGMA table_info(recordatorio)").fetchall()
        if not columns:
            return

        existing = {col[1] for col in columns}
        if "estado" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE recordatorio ADD COLUMN estado VARCHAR DEFAULT 'pendiente'"
            )
        if "monto_cobrado" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE recordatorio ADD COLUMN monto_cobrado FLOAT DEFAULT 0"
            )
        if "fecha_cobro" not in existing:
            conn.exec_driver_sql(
                "ALTER TABLE recordatorio ADD COLUMN fecha_cobro VARCHAR"
            )

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _ensure_recordatorio_columns()

def get_session():
    with Session(engine) as session:
        yield session