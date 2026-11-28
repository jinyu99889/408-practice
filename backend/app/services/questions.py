from sqlalchemy import text
from sqlalchemy.orm import Session

from app.error_codes import ErrorCode
from app.errors import AppError
from app.schemas.question import Answer
from app.services.json_fields import decode_json


# 只投影答案相关的四列，草稿题在 SQL 里就过滤掉，不给上层留"忘了判断状态"的机会。
QUESTION_ANSWER_SQL = text(
    """
    SELECT answer_choice, answer_text, analysis, knowledge_tags
    FROM question
    WHERE id = :question_id AND status = 'approved'
    """
)


def question_answer(db: Session, question_id: int) -> Answer:
    """返回一道已审核题的答案与解析；草稿题与不存在的题同样按 404 处理。"""
    row = db.execute(
        QUESTION_ANSWER_SQL, {"question_id": question_id}
    ).mappings().first()
    if row is None:
        raise AppError(ErrorCode.QUESTION_NOT_FOUND, "题目不存在", {})

    # 响应模型本身不接受多余字段，答案出口再也带不出题面信息。
    return Answer(
        answer_choice=decode_json(row["answer_choice"], None),
        answer_text=row["answer_text"],
        analysis=row["analysis"],
        knowledge_tags=decode_json(row["knowledge_tags"], []),
    )
