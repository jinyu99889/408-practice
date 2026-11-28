from typing import Annotated

from fastapi import APIRouter, Path, Request
from fastapi.responses import FileResponse

from app.config import Settings
from app.services.media import resolve_media_path

# 题面里的 stem_images / options.image 直接存本路由的地址，浏览器当普通 <img> 取。
router = APIRouter()


@router.get("/media/{paper_id}/{file_name}", tags=["media"])
def get_media(
    paper_id: Annotated[int, Path(gt=0)],
    file_name: str,
    request: Request,
) -> FileResponse:
    """返回某张卷目录下的题目插图，路径不合规或文件不存在都按 404 处理。"""
    settings: Settings = request.app.state.settings
    path, media_type = resolve_media_path(settings.data_dir / "media", paper_id, file_name)
    return FileResponse(path, media_type=media_type)
