from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ChatThread(Base):
    """保存一道题在普通卷或错题本场景中的伴读对话。"""

    __tablename__ = "chat_thread"
    __table_args__ = (
        CheckConstraint("scene IN ('paper', 'wrongbook')"),
        # 同一道题在同一场景下只保留一段连续对话。
        UniqueConstraint("question_id", "scene"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 对话对应的题目（question.id），题目删除时对话级联删除。
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    # 对话场景：'paper' = 普通卷，'wrongbook' = 错题本；同一道题在同一场景下只保留一段对话。
    scene: Mapped[str] = mapped_column(Text, nullable=False, server_default="paper")
    # 对话创建时间，带时区；由业务层写入。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 最后有消息更新的时间，带时区；由业务层写入。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)