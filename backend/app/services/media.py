import re
from pathlib import Path

from app.error_codes import ErrorCode
from app.errors import AppError

# 文件名白名单：屏蔽路径分隔符、前导点、控制字符，把穿越挡在第一道门。
_MEDIA_NAME = re.compile(r"^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9]+)?$")

# 只认这四种图片后缀，Content-Type 由后缀决定，不读文件头。
_MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _not_found() -> AppError:
    """返回统一的图片缺失错误，避免把非法路径与真实缺失区分给调用方。"""
    return AppError(ErrorCode.MEDIA_NOT_FOUND, "图片不存在", {})


def resolve_media_path(
    media_root: Path, paper_id: int, file_name: str
) -> tuple[Path, str]:
    """把卷号与文件名解析成卷目录内的真实图片路径，并给出 Content-Type。

    白名单是第一道门，resolve() 之后再回查父目录是第二道门：即使正则被绕过，
    解析结果也必须仍然落在 data/media/{paper_id}/ 里。
    """
    if not _MEDIA_NAME.fullmatch(file_name):
        raise _not_found()

    media_type = _MEDIA_TYPES.get(Path(file_name).suffix.lower())
    if media_type is None:
        raise _not_found()

    paper_dir = (media_root / str(paper_id)).resolve()
    candidate = (paper_dir / file_name).resolve()
    if paper_dir not in candidate.parents or not candidate.is_file():
        raise _not_found()
    return candidate, media_type
