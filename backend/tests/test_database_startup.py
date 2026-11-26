from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.dialects import postgresql

from app.models import Base

def test_packaged_schema_matches_repository_schema():
    backend_root = Path(__file__).resolve().parents[1]
    assert (backend_root / "app" / "resources" / "schema.sql").read_bytes() == (
        backend_root.parent / "db" / "schema.sql"
    ).read_bytes()

@pytest.mark.usefixtures("initialized_test_db")
def test_startup_creates_schema_defaults_and_local_secrets(initialized_test_db, test_engine):
    data_dir = initialized_test_db.state.settings.data_dir
    assert (data_dir / "uploads").is_dir()
    assert (data_dir / "media").is_dir()
    key = (data_dir / "secret.key").read_bytes()
    assert len(key) == 44

    with test_engine.connect() as connection:
        names = connection.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        ).scalars().all()
        defaults = connection.execute(
            text("SELECT key, value FROM app_setting ORDER BY key")
        ).all()
    assert len(names) == 12
    assert defaults == [
        ("ai.api_key", ""),
        ("ai.base_url", "https://api.deepseek.com/v1"),
        ("ai.chat_model", "deepseek-chat"),
        ("ai.vision_model", "deepseek-vl"),
    ]
    inspector = inspect(test_engine)
    assert set(inspector.get_table_names()) == set(Base.metadata.tables)
    for table_name, model_table in Base.metadata.tables.items():
        database_columns = {
            column["name"]: column["type"]
            for column in inspector.get_columns(table_name)
        }
        assert set(database_columns) == set(model_table.columns.keys())
        for column in model_table.columns:
            assert database_columns[column.name].compile(
                dialect=postgresql.dialect()
            ) == column.type.compile(dialect=postgresql.dialect())
        assert len(inspector.get_check_constraints(table_name)) == sum(
            constraint.__class__.__name__ == "CheckConstraint"
            for constraint in model_table.constraints
        )
        assert len(inspector.get_foreign_keys(table_name)) == sum(
            constraint.__class__.__name__ == "ForeignKeyConstraint"
            for constraint in model_table.constraints
        )
        assert len(inspector.get_unique_constraints(table_name)) == sum(
            constraint.__class__.__name__ == "UniqueConstraint"
            for constraint in model_table.constraints
        )
        assert {
            index["name"]
            for index in inspector.get_indexes(table_name)
            if not index.get("duplicates_constraint")
        } == {
            index.name for index in model_table.indexes
        }

@pytest.mark.usefixtures("initialized_test_db")
def test_restart_marks_interrupted_jobs_and_attempts(initialized_test_db, test_engine):
    with test_engine.begin() as connection:
        connection.exec_driver_sql(
            "INSERT INTO paper (title, created_at, updated_at) VALUES ('test', now(), now())"
        )
        connection.exec_driver_sql(
            "INSERT INTO import_job (paper_id, file_name, stored_path, file_type, status, created_at) "
            "VALUES (1, 'test.pdf', '/tmp/test.pdf', 'pdf', 'processing', now())"
        )
        connection.exec_driver_sql(
            "INSERT INTO exam_attempt (paper_id, duration_sec, started_at, deadline_at, created_at) "
            "VALUES (1, 60, now(), now(), now())"
        )
    from app.db import initialize_application

    initialize_application(initialized_test_db.state.settings, test_engine)
    with test_engine.connect() as connection:
        job = connection.execute(
            text("SELECT status, error_message FROM import_job")
        ).one()
        attempt_status = connection.execute(
            text("SELECT status FROM exam_attempt")
        ).scalar_one()
    assert job == ("failed", "解析中断，请重试")
    assert attempt_status == "abandoned"
