from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ImportJob(Base):
    """跟踪一次上传解析任务及当前处理阶段、失败信息。"""

    __tablename__ = "import_job"
    __table_args__ = (
        CheckConstraint("file_type IN ('pdf', 'png', 'jpg', 'webp')"),
        CheckConstraint("status IN ('pending', 'processing', 'waiting_review', 'completed', 'failed', 'cancelled')"),
        CheckConstraint("stage IS NULL OR stage IN ('extract', 'segment', 'structure', 'generate_answer')"),
        CheckConstraint("has_answer IS NULL OR has_answer IN ('yes', 'no', 'mixed')"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    # 一次上传会创建一张新卷，因此 paper 与 import_job 一对一。
    paper_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("paper.id", ondelete="CASCADE"), unique=True, nullable=False)
    # 用户上传的原始文件名，供审核页展示。
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    # 文件在本机 data 目录下的存储路径。
    stored_path: Mapped[str] = mapped_column(Text, nullable=False)
    # 文件类型：'pdf' / 'png' / 'jpg' / 'webp'。
    file_type: Mapped[str] = mapped_column(Text, nullable=False)
    # 任务状态：'pending' 排队 / 'processing' 处理中 / 'waiting_review' 等待人工审核 / 'completed' 完成 / 'failed' 失败 / 'cancelled' 取消。
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default="pending")
    # 当前处理阶段：'extract' 抽取正文 / 'segment' 切分题目 / 'structure' 结构化字段 / 'generate_answer' 生成答案；仅在处理中有值。
    stage: Mapped[str | None] = mapped_column(Text)
    # 原始文档是否自带答案：'yes' / 'no' / 'mixed' 部分含；识别前为空。
    has_answer: Mapped[str | None] = mapped_column(Text)
    # 解析出的题目数量，解析完成后回填。
    question_count: Mapped[int | None] = mapped_column(Integer)
    # 失败原因，status='failed' 时记录，便于排查。
    error_message: Mapped[str | None] = mapped_column(Text)
    # 任务创建（入队）时间，带时区。
    created_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)
    # 开始处理时间，带时区；进入 processing 时写入。
    started_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    # 结束时间，带时区；completed / failed / cancelled 时写入。
    finished_at: Mapped[object | None] = mapped_column(DateTime(timezone=True))