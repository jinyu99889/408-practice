from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Index, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ChatMessage(Base):
    """保存伴读对话中的单条用户或助手消息。"""

    __tablename__ = "chat_message"
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')"),
        CheckConstraint("mode IS NULL OR mode IN ('guide', 'learn')"),
        # 按对话顺序读取消息时，可由 thread_id 和 id 索引支持。
        Index("idx_chat_message_thread", "thread_id", "id"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 所属伴读对话（chat_thread.id），删除对话时级联删除本消息。
    thread_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chat_thread.id", ondelete="CASCADE"), nullable=False)
    # 消息发送方：'user' = 用户提问，'assistant' = AI 伴读回复。
    role: Mapped[str] = mapped_column(Text, nullable=False)
    # AI 回复采用的伴读模式：'guide' = 引导，'learn' = 讲解；user 消息不区分模式，故为空。
    mode: Mapped[str | None] = mapped_column(Text)
    # 消息正文内容。
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 消息创建（发送）时间，带时区；由业务层写入，数据库无默认值。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)