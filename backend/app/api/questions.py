from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.question import Answer
from app.services.questions import question_answer

# 答案只从这一个路由吐出去，题面接口一律不带答案字段。
router = APIRouter()


@router.get("/questions/{question_id}/answer", response_model=Answer, tags=["questions"])
def get_answer(
    question_id: Annotated[int, Path(gt=0)],
    db: Session = Depends(get_db),
) -> Answer:
    """返回一道已审核题的答案、解析与知识点。"""
    return question_answer(db, question_id)
