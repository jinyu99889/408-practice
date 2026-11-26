from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class WrongItem(Base):
    """表示一道题已加入错题本；移除时删除此条记录。"""

    __tablename__ = "wrong_item"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 加入错题本的题目（question.id）；唯一约束保证同一道题不会重复加入，删题时记录级联删除。
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("question.id", ondelete="CASCADE"), unique=True, nullable=False)
    # 加入错题本的时间，带时区。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)