from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class QuestionOption(BaseModel):
    """客观题选项的公开结构。"""

    model_config = ConfigDict(extra="forbid")

    key: str
    text: str
    image: str | None


class QuestionPart(BaseModel):
    """主观题小问的公开结构。"""

    model_config = ConfigDict(extra="forbid")

    text: str
    images: list[str]


class QuestionStub(BaseModel):
    """做题页需要的题面字段，不包含答案、解析或知识点。"""

    id: int
    seq_no: int
    qtype: str
    subject: str
    score: int
    stem: str
    stem_images: list[str]
    options: list[QuestionOption]
    parts: list[QuestionPart] | None


class PaperDetail(BaseModel):
    """做题页一次加载的整张已发布试卷。"""

    id: int
    title: str
    year: int | None
    total_score: int
    questions: list[QuestionStub]
