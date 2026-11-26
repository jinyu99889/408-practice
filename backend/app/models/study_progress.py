from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class StudyProgress(Base):
    """记录每张普通卷的当前学习题号和最近学习时间。"""

    __tablename__ = "study_progress"
    # 关联的普通卷（paper.id），兼作主键，一张卷仅一条进度；删卷时进度随之删除。
    paper_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper.id", ondelete="CASCADE"), primary_key=True)
    # 当前学习进度：下一道要做的题的 seq_no（从 1 开始）。
    current_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    # 最近一次学习时间，带时区；用于"继续上次做题"定位。
    last_studied_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))