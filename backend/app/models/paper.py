from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Paper(Base):
    """表示一张真题卷或自定义练习卷。"""

    __tablename__ = "paper"
    # 数据库拒绝未知卷类型和状态，避免接口写入无效生命周期值。
    __table_args__ = (
        CheckConstraint("kind IN ('exam', 'custom')"),
        CheckConstraint("status IN ('draft', 'published')"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 卷名，如"2025 年统考真题"。
    title: Mapped[str] = mapped_column(Text, nullable=False)
    # 考试年份；自定义练习卷可为空。
    year: Mapped[int | None] = mapped_column(Integer)
    # 卷类型：'exam' = 真题卷，'custom' = 自定义练习卷。
    kind: Mapped[str] = mapped_column(Text, nullable=False, server_default="exam")
    # 卷状态：'draft' = 草稿未发布，'published' = 已发布可做题。
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="draft")
    # 创建时间，带时区；由业务层写入。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 更新时间，带时区；由业务层写入。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)