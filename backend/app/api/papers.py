from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.paper import PaperSummary
from app.services.papers import paper_summaries

# 试卷列表只读已发布试卷，统计逻辑统一放在服务层，避免路由混入 SQL 细节。
router = APIRouter()


@router.get("/papers", response_model=list[PaperSummary], tags=["papers"])
def list_papers(db: Session = Depends(get_db)) -> list[PaperSummary]:
    """返回最新的已发布试卷及其题目、考试汇总信息。"""
    return paper_summaries(db)
