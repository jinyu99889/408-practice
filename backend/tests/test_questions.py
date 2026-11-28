import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import create_app


@pytest.fixture
def question_client() -> Iterator[tuple[TestClient, Engine]]:
    """只建答案接口用到的字段；#41 换成 PostgreSQL 共享 fixture 后删除。"""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql(
            "CREATE TABLE question (id INTEGER PRIMARY KEY, stem TEXT, "
            "options TEXT NOT NULL DEFAULT '[]', answer_choice TEXT, answer_text TEXT, "
            "analysis TEXT, knowledge_tags TEXT NOT NULL DEFAULT '[]', "
            "status TEXT NOT NULL)"
        )

    application = create_app(enable_startup=False)

    def override_get_db() -> Iterator[Session]:
        with Session(engine) as db:
            yield db

    application.dependency_overrides[get_db] = override_get_db
    with TestClient(application) as client:
        yield client, engine
    engine.dispose()


def _insert_question(
    engine: Engine,
    *,
    question_id: int,
    status: str = "approved",
    answer_choice: list[str] | None = None,
    answer_text: str | None = None,
    analysis: str | None = None,
    knowledge_tags: list[str] | None = None,
) -> None:
    """写入一道题；题面字段故意留值，用于验证答案接口不会把它们带出去。"""
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO question (id, stem, options, answer_choice, answer_text, "
                "analysis, knowledge_tags, status) "
                "VALUES (:id, '题面不应出现在答案接口里', '[]', :answer_choice, "
                ":answer_text, :analysis, :knowledge_tags, :status)"
            ),
            {
                "id": question_id,
                "answer_choice": json.dumps(answer_choice, ensure_ascii=False)
                if answer_choice is not None
                else None,
                "answer_text": answer_text,
                "analysis": analysis,
                "knowledge_tags": json.dumps(knowledge_tags or [], ensure_ascii=False),
                "status": status,
            },
        )


def test_get_answer_returns_choice_array_for_objective_question(question_client) -> None:
    """客观题返回选项数组，答案文本为 null。"""
    client, engine = question_client
    _insert_question(
        engine,
        question_id=1,
        answer_choice=["A"],
        analysis="栈是后进先出的线性表……",
        knowledge_tags=["栈", "存储结构"],
    )

    response = client.get("/api/v1/questions/1/answer")

    assert response.status_code == 200
    assert response.json() == {
        "answer_choice": ["A"],
        "answer_text": None,
        "analysis": "栈是后进先出的线性表……",
        "knowledge_tags": ["栈", "存储结构"],
    }


def test_get_answer_returns_reference_text_for_subjective_question(question_client) -> None:
    """主观题返回参考答案，选项数组为 null。"""
    client, engine = question_client
    _insert_question(
        engine, question_id=2, answer_text="参考答案：先建堆再调整。"
    )

    response = client.get("/api/v1/questions/2/answer")

    assert response.status_code == 200
    assert response.json()["answer_text"] == "参考答案：先建堆再调整。"
    assert response.json()["answer_choice"] is None


def test_get_answer_hides_draft_question(question_client) -> None:
    """草稿题按不存在处理，不泄露它已经有答案。"""
    client, engine = question_client
    _insert_question(engine, question_id=3, status="draft", answer_choice=["B"])

    response = client.get("/api/v1/questions/3/answer")

    assert response.status_code == 404
    assert response.json() == {
        "code": "QUESTION_NOT_FOUND",
        "message": "题目不存在",
        "details": {},
    }


def test_get_answer_returns_unified_not_found_for_missing_question(question_client) -> None:
    """不存在的题返回统一错误结构。"""
    client, _engine = question_client

    response = client.get("/api/v1/questions/999999/answer")

    assert response.status_code == 404
    assert response.json()["code"] == "QUESTION_NOT_FOUND"


def test_get_answer_keeps_empty_knowledge_tags_as_array(question_client) -> None:
    """没有知识点时给空数组，不给 null。"""
    client, engine = question_client
    _insert_question(engine, question_id=4, answer_choice=["C"], knowledge_tags=[])

    response = client.get("/api/v1/questions/4/answer")

    assert response.status_code == 200
    assert response.json()["knowledge_tags"] == []


def test_get_answer_allows_null_analysis(question_client) -> None:
    """解析为空时照常返回，不报错。"""
    client, engine = question_client
    _insert_question(engine, question_id=5, answer_choice=["D"], analysis=None)

    response = client.get("/api/v1/questions/5/answer")

    assert response.status_code == 200
    assert response.json()["analysis"] is None


def test_get_answer_preserves_multi_choice_order(question_client) -> None:
    """多选题选项按入库顺序原样返回，排序只在判分时做。"""
    client, engine = question_client
    _insert_question(engine, question_id=6, answer_choice=["C", "A"])

    response = client.get("/api/v1/questions/6/answer")

    assert response.json()["answer_choice"] == ["C", "A"]


def test_get_answer_never_exposes_stem_fields(question_client) -> None:
    """答案接口只回四个契约字段，题面内容一个都不带。"""
    client, engine = question_client
    _insert_question(engine, question_id=7, answer_choice=["A"])

    body = client.get("/api/v1/questions/7/answer").json()

    assert list(body) == ["answer_choice", "answer_text", "analysis", "knowledge_tags"]
    assert "题面不应出现在答案接口里" not in json.dumps(body, ensure_ascii=False)
