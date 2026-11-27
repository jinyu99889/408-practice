from collections.abc import Iterator
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import create_app


@pytest.fixture
def paper_client() -> Iterator[tuple[TestClient, Engine, list[str]]]:
    """为列表接口创建隔离的内存数据库，避免测试产生持久化垃圾数据。"""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # 只建查询涉及的三张轻量表；接口查询口径与 PostgreSQL 正式表保持一致。
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE paper (id INTEGER PRIMARY KEY, title TEXT NOT NULL, "
            "year INTEGER, status TEXT NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE question (id INTEGER PRIMARY KEY, paper_id INTEGER NOT NULL, "
            "score INTEGER NOT NULL, status TEXT NOT NULL)"
        )
        connection.exec_driver_sql(
            "CREATE TABLE exam_attempt (id INTEGER PRIMARY KEY, paper_id INTEGER NOT NULL, "
            "status TEXT NOT NULL, submitted_at TEXT, total_score INTEGER)"
        )

    statements: list[str] = []

    def capture_statement(_connection, _cursor, statement, _parameters, _context, _many):
        """记录 SQL，验证接口没有退化成逐张试卷查询。"""
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", capture_statement)
    app = create_app(enable_startup=False)

    def override_get_db() -> Iterator[Session]:
        with Session(engine) as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, engine, statements
    event.remove(engine, "before_cursor_execute", capture_statement)
    engine.dispose()


def _insert_paper(
    engine: Engine, paper_id: int, title: str, year: int | None, status: str
) -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO paper (id, title, year, status) "
                "VALUES (:id, :title, :year, :status)"
            ),
            {"id": paper_id, "title": title, "year": year, "status": status},
        )


def test_list_papers_aggregates_only_visible_content_and_completed_attempts(
    paper_client,
) -> None:
    """验证发布状态、题目审核状态和考试完成状态的统计口径。"""
    client, engine, statements = paper_client
    _insert_paper(engine, 1, "2024 paper", 2024, "published")
    _insert_paper(engine, 2, "2023 paper", 2023, "published")
    _insert_paper(engine, 3, "draft paper", 2025, "draft")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO question (id, paper_id, score, status) VALUES "
                "(1, 1, 3, 'approved'), (2, 1, 4, 'approved'), "
                "(3, 1, 99, 'draft'), (4, 3, 50, 'approved')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO exam_attempt (id, paper_id, status, submitted_at, total_score) VALUES "
                "(1, 1, 'submitted', '2026-11-20T13:00:00+00:00', 60), "
                "(2, 1, 'auto_submitted', '2026-11-20T14:32:10+00:00', 78), "
                "(3, 1, 'abandoned', '2026-11-20T15:00:00+00:00', 140), "
                "(4, 1, 'in_progress', NULL, NULL)"
            )
        )

    statements.clear()
    response = client.get("/api/v1/papers")

    assert response.status_code == 200
    body = response.json()
    assert body == [
        {
            "id": 1,
            "title": "2024 paper",
            "year": 2024,
            "question_count": 2,
            "total_score": 7,
            "last_exam_score": 78,
            "last_exam_at": "2026-11-20T14:32:10Z",
            "exam_count": 2,
        },
        {
            "id": 2,
            "title": "2023 paper",
            "year": 2023,
            "question_count": 0,
            "total_score": 0,
            "last_exam_score": None,
            "last_exam_at": None,
            "exam_count": 0,
        },
    ]
    assert datetime.fromisoformat(
        body[0]["last_exam_at"].replace("Z", "+00:00")
    ) == datetime.fromisoformat("2026-11-20T14:32:10+00:00")
    assert len(
        [
            statement
            for statement in statements
            if statement.lstrip().upper().startswith("SELECT")
        ]
    ) == 1


def test_list_papers_returns_at_most_12_sorted_published_papers(paper_client) -> None:
    """验证年份倒序并限制最多返回 12 张试卷。"""
    client, engine, _statements = paper_client
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO paper (id, title, year, status) VALUES "
                + ", ".join(
                    f"({i}, 'paper {i}', {2000 + i}, 'published')"
                    for i in range(1, 15)
                )
                + ", (99, 'hidden', 2100, 'draft')"
            )
        )

    response = client.get("/api/v1/papers")

    assert response.status_code == 200
    assert len(response.json()) == 12
    assert [paper["year"] for paper in response.json()] == list(range(2014, 2002, -1))


def test_list_papers_returns_empty_array_when_no_papers_are_published(
    paper_client,
) -> None:
    """没有已发布试卷时返回空数组。"""
    client, engine, _statements = paper_client
    _insert_paper(engine, 1, "draft", 2024, "draft")

    response = client.get("/api/v1/papers")

    assert response.status_code == 200
    assert response.json() == []


def test_paper_summary_fields_keep_contract_order() -> None:
    """验证响应模型字段顺序不会因后续扩展而改变。"""
    from app.schemas.paper import PaperSummary

    assert list(PaperSummary.model_fields) == [
        "id",
        "title",
        "year",
        "question_count",
        "total_score",
        "last_exam_score",
        "last_exam_at",
        "exam_count",
    ]
