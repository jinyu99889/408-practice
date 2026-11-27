from datetime import datetime

from pydantic import BaseModel


class PaperSummary(BaseModel):
    """试卷列表卡片所需的汇总字段，字段顺序即接口返回顺序。"""

    # 试卷基础信息；自定义试卷可能没有年份。
    id: int
    title: str
    year: int | None
    # 只统计 status = approved 的题目。
    question_count: int
    total_score: int
    # 没有已提交考试时，两项成绩信息为空。
    last_exam_score: int | None
    last_exam_at: datetime | None
    # 只统计 submitted 和 auto_submitted 两种考试状态。
    exam_count: int
