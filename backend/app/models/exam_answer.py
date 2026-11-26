from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Identity, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ExamAnswer(Base):
    """保存某场考试中一道题的作答、标记和主观题自评分。"""

    __tablename__ = "exam_answer"
    __table_args__ = (
        CheckConstraint("choice IS NULL OR jsonb_typeof(choice) = 'array'"),
        CheckConstraint("self_score IS NULL OR self_score >= 0"),
        # 一场考试中每道题只对应一条作答。
        UniqueConstraint("attempt_id", "question_id"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 所属考试（exam_attempt.id），删除考试记录时作答级联删除。
    attempt_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("exam_attempt.id", ondelete="CASCADE"), nullable=False)
    # 作答的题目（question.id），删题时作答级联删除。
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    # 客观题作答：选项下标数组，如 [0, 2]；未答为空。
    choice: Mapped[list | None] = mapped_column(JSONB)
    # 是否已作答（做过该题）。
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # 主观题自评分（>= 0），考生交卷前填写。
    self_score: Mapped[int | None] = mapped_column(Integer)
    # 是否在答题卡上打了"标记"，交卷后仍保留。
    is_marked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # 客观题是否判对，交卷后统一判分并回填；主观题为空。
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    # 最近作答更新时间，带时区。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)