from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Identity, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class StudyAnswer(Base):
    """保存一道题在普通卷或错题本中的学习作答状态。"""

    __tablename__ = "study_answer"
    __table_args__ = (
        CheckConstraint("scene IN ('paper', 'wrongbook')"),
        CheckConstraint("choice IS NULL OR jsonb_typeof(choice) = 'array'"),
        # 两个场景的作答相互独立，但各场景内每题最多一行。
        UniqueConstraint("question_id", "scene"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 作答的题目（question.id），删题时记录级联删除。
    question_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("question.id", ondelete="CASCADE"), nullable=False)
    # 作答场景：'paper' = 普通卷，'wrongbook' = 错题本；错题本作答独立保存。
    scene: Mapped[str] = mapped_column(Text, nullable=False, server_default="paper")
    # 作答选择：选项下标数组，如 [0, 2]；未答为空。
    choice: Mapped[list | None] = mapped_column(JSONB)
    # 是否判对，学习模式作答后即时回填。
    is_correct: Mapped[bool | None] = mapped_column(Boolean)
    # 是否已作答。
    is_done: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # 是否在答题卡上打了"标记"。
    is_marked: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # 最近作答更新时间，带时区。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)