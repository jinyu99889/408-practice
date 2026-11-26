from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 SQLAlchemy ORM 模型共享的声明式元数据基类。"""

    pass
