import json
from typing import Any


def decode_json(value: Any, default: Any) -> Any:
    """把查询结果里的 JSON 字段还原成 Python 值。

    PostgreSQL 的 JSONB 由驱动直接解码，走到最后一行原样返回；SQLite 测试库把
    同一列存成 TEXT，需要再解一次。等 #41 把测试库换成 PostgreSQL 后，本模块
    和所有调用点都可以整体删掉。
    """
    if value is None:
        return default
    if isinstance(value, str):
        return json.loads(value)
    return value
