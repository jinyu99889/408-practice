from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.paper import PaperSummary


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
