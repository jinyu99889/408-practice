from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.paper import PaperDetail, PaperSummary
from app.services.papers import paper_detail, paper_summaries

# 试卷列表只读已发布试卷，统计逻辑统一放在服务层，避免路由混入 SQL 细节。
router = APIRouter()


@router.get("/papers", response_model=list[PaperSummary], tags=["papers"])
def list_papers(db: Session = Depends(get_db)) -> list[PaperSummary]:
    """返回最新的已发布试卷及其题目、考试汇总信息。"""
    return paper_summaries(db)


@router.get("/papers/{paper_id}", response_model=PaperDetail, tags=["papers"])
def get_paper(
    paper_id: Annotated[int, Path(gt=0, le=2**63 - 1)],
    db: Session = Depends(get_db),
) -> PaperDetail:
    """返回一张已发布试卷的全部已审核题面。"""
    return paper_detail(db, paper_id)
