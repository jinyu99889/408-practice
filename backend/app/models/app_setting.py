from sqlalchemy import Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class AppSetting(Base):
    """保存单用户应用配置；敏感配置以密文写入 value。"""

    __tablename__ = "app_setting"
    # 配置键名，如 api_base_url、api_key、chat_model、vision_model 等。
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    # 配置值：敏感项（如密钥）为 Fernet 密文，普通项为明文。
    value: Mapped[str] = mapped_column(Text, nullable=False)
    # 标记 value 是否为 Fernet 密文，避免普通配置被误解密。
    is_encrypted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    # 最近更新时间，带时区。
    updated_at: Mapped[object] = mapped_column(DateTime(timezone=True), nullable=False)