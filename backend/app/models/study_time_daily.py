from datetime import date
from sqlalchemy import CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class StudyTimeDaily(Base):
    """按本地自然日累计学习时长，seconds 的单位为秒。"""

    __tablename__ = "study_time_daily"
    __table_args__ = (CheckConstraint("seconds >= 0"),)
    # 本地自然日（YYYY-MM-DD），作为主键按天一行记录。
    study_date: Mapped[date] = mapped_column(primary_key=True)
    # 当天累计学习秒数，须 >= 0；每段学习结束累加。
    seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")