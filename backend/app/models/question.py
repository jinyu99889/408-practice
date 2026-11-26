from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Question(Base):
    """保存题干、图片、选项、答案和审核状态，一道题对应一行。"""

    __tablename__ = "question"
    __table_args__ = (
        CheckConstraint("qtype IN ('single', 'multi', 'judge', 'short', 'calc')"),
        CheckConstraint("score > 0"),
        # JSONB 字段在数据库层约束为数组，避免对象或标量混入。
        CheckConstraint("jsonb_typeof(stem_images) = 'array'"),
        CheckConstraint("jsonb_typeof(options) = 'array'"),
        CheckConstraint("parts IS NULL OR jsonb_typeof(parts) = 'array'"),
        CheckConstraint("answer_choice IS NULL OR jsonb_typeof(answer_choice) = 'array'"),
        CheckConstraint("jsonb_typeof(knowledge_tags) = 'array'"),
        CheckConstraint("status IN ('draft', 'approved')"),
        UniqueConstraint("paper_id", "seq_no"),
        Index("idx_question_paper_status", "paper_id", "status"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 所属试卷（paper.id），删卷时题目级联删除。
    paper_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper.id", ondelete="CASCADE"), nullable=False)
    # 题号，同一张卷内从 1 起唯一，按此顺序展示题目。
    seq_no: Mapped[int] = mapped_column(Integer, nullable=False)
    # 题型：'single' 单选 / 'multi' 多选 / 'judge' 判断 / 'short' 简答 / 'calc' 计算。
    qtype: Mapped[str] = mapped_column(Text, nullable=False)
    # 所属学科（如 数据结构、操作系统、计算机组成原理、计算机网络）。
    subject: Mapped[str] = mapped_column(Text, nullable=False)
    # 本题分值，须大于 0。
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    # 题干文本。
    stem: Mapped[str] = mapped_column(Text, nullable=False)
    # 题干插图地址数组，顺序与题干中图片出现顺序一致。
    stem_images: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # 选项数组（客观题），下标从 0 起，与 answer_choice 下标对应。
    options: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # 主观题分小题结构（数组），非主观题为空。
    parts: Mapped[list | None] = mapped_column(JSONB)
    # 客观题正确答案：选项下标数组，如 [0, 2]。
    answer_choice: Mapped[list | None] = mapped_column(JSONB)
    # 主观题参考答案文本。
    answer_text: Mapped[str | None] = mapped_column(Text)
    # 题目解析/讲解文本。
    analysis: Mapped[str | None] = mapped_column(Text)
    # 知识点标签数组，用于错题归类等统计。
    knowledge_tags: Mapped[list] = mapped_column(JSONB, nullable=False, server_default="[]")
    # 审核状态：'draft' = 草稿（答案可不完整），'approved' = 已审核通过；完整性由业务层校验。
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    # 来源导入任务（import_job.id），任务删除时置空（SET NULL）。
    import_job_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("import_job.id", ondelete="SET NULL"))
    # 创建时间，带时区；由业务层写入。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 更新时间，带时区；由业务层写入。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)