from sqlalchemy import text
from sqlalchemy.orm import Session

from app.errors import AppError
from app.error_codes import ErrorCode
from app.schemas.paper import PaperDetail, PaperSummary, QuestionStub
from app.services.json_fields import decode_json


# 列表页只需要固定数量的最新试卷；所有统计在一条 SQL 中完成，避免逐卷查询。
PAPER_SUMMARIES_SQL = text(
    """
    SELECT p.id, p.title, p.year,
           -- draft 题不计入已启用题目数和总分。
           COUNT(q.id) AS question_count,
           COALESCE(SUM(q.score), 0) AS total_score,
           -- 成绩只取已交卷记录；按交卷时间倒序获取最近一次成绩。
           (SELECT a.total_score FROM exam_attempt a
              WHERE a.paper_id = p.id
                AND a.status IN ('submitted', 'auto_submitted')
              ORDER BY a.submitted_at DESC LIMIT 1) AS last_exam_score,
           (SELECT a.submitted_at FROM exam_attempt a
              WHERE a.paper_id = p.id
                AND a.status IN ('submitted', 'auto_submitted')
              ORDER BY a.submitted_at DESC LIMIT 1) AS last_exam_at,
           (SELECT COUNT(*) FROM exam_attempt a
              WHERE a.paper_id = p.id
                AND a.status IN ('submitted', 'auto_submitted')) AS exam_count
    FROM paper p
    -- LEFT JOIN 保留没有已审核题目的已发布试卷，统计结果为 0。
    LEFT JOIN question q
      ON q.paper_id = p.id AND q.status = 'approved'
    -- 未发布的草稿卷对前端不可见。
    WHERE p.status = 'published'
    GROUP BY p.id
    ORDER BY p.year DESC, p.id DESC
    -- 暂不引入分页参数，接口无感知地限制首屏数据量。
    LIMIT 12
    """
)


def paper_summaries(db: Session) -> list[PaperSummary]:
    """用一条聚合查询返回最新 12 张已发布试卷。"""
    rows = db.execute(PAPER_SUMMARIES_SQL).mappings()
    # 显式按响应模型转换，保证字段名、类型和对外顺序符合接口契约。
    return [PaperSummary.model_validate(row) for row in rows]


PAPER_DETAIL_SQL = text(
    """
    SELECT p.id, p.title, p.year,
           COALESCE(SUM(q.score) OVER (), 0) AS total_score,
           q.id AS question_id, q.seq_no, q.qtype, q.subject, q.score,
           q.stem, q.stem_images, q.options, q.parts
    FROM paper p
    LEFT JOIN question q
      ON q.paper_id = p.id AND q.status = 'approved'
    WHERE p.id = :paper_id AND p.status = 'published'
    ORDER BY q.seq_no ASC
    """
)


def paper_detail(db: Session, paper_id: int) -> PaperDetail:
    """用一次投影查询拼出一张已发布试卷的题面。"""
    rows = list(db.execute(PAPER_DETAIL_SQL, {"paper_id": paper_id}).mappings())
    if not rows:
        raise AppError(ErrorCode.PAPER_NOT_FOUND, "试卷不存在", {})

    first = rows[0]
    questions: list[QuestionStub] = []
    for row in rows:
        if row["question_id"] is None:
            continue
        questions.append(
            QuestionStub(
                id=row["question_id"],
                seq_no=row["seq_no"],
                qtype=row["qtype"],
                subject=row["subject"],
                score=row["score"],
                stem=row["stem"],
                stem_images=decode_json(row["stem_images"], []),
                options=decode_json(row["options"], []),
                parts=decode_json(row["parts"], None),
            )
        )

    # TODO: 45 题 PostgreSQL 无缓存中位数为 6.48ms，真实卷数据到位后再评估缓存。
    return PaperDetail(
        id=first["id"],
        title=first["title"],
        year=first["year"],
        total_score=first["total_score"],
        questions=questions,
    )
