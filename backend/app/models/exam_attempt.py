from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Integer, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ExamAttempt(Base):
    """记录一次不可暂停的考试及其计时、交卷和得分状态。"""

    __tablename__ = "exam_attempt"
    __table_args__ = (
        CheckConstraint("duration_sec > 0"),
        # 离开或重启中断的考试记为 abandoned，不提供暂停状态。
        CheckConstraint("status IN ('in_progress', 'submitted', 'auto_submitted', 'abandoned')"),
        Index(
            "idx_exam_attempt_paper",
            "paper_id",
            "started_at",
            postgresql_ops={"started_at": "DESC"},
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 考的是哪张卷（paper.id），删卷时考试记录级联删除。
    paper_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper.id", ondelete="CASCADE"), nullable=False)
    # 考试时长（秒），须大于 0；考试不可暂停。
    duration_sec: Mapped[int] = mapped_column(Integer, nullable=False)
    # 考试状态：'in_progress' 进行中 / 'submitted' 已交卷 / 'auto_submitted' 到时自动交卷 / 'abandoned' 中断弃考。
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="in_progress")
    # 开考时间，带时区。
    started_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 截止时间 = started_at + duration_sec，到时自动交卷。
    deadline_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 实际交卷时间，带时区；未交卷为空。
    submitted_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    # 实际用时（秒），交卷后回填。
    elapsed_sec: Mapped[int | None] = mapped_column(Integer)
    # 客观题得分，交卷判分后回填。
    objective_score: Mapped[int | None] = mapped_column(Integer)
    # 主观题自评分合计，交卷后回填。
    subjective_score: Mapped[int | None] = mapped_column(Integer)
    # 总分 = 客观题 + 主观题得分，交卷后回填。
    total_score: Mapped[int | None] = mapped_column(Integer)
    # 记录创建时间（开考即建），带时区。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)