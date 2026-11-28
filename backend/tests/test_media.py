import base64
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.error_codes import ErrorCode
from app.errors import AppError
from app.main import create_app
from app.services.media import resolve_media_path

# 真实的 1×1 PNG，保证 <img> 能显示而不只是字节能对上。
PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
JPG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01" + b"\x00" * 8


@pytest.fixture
def media_client(tmp_path: Path) -> Iterator[tuple[TestClient, Path]]:
    """用临时数据目录启动应用，避免测试读写仓库里的 data/。"""
    data_dir = tmp_path / "data"
    media_root = data_dir / "media"
    (media_root / "1").mkdir(parents=True)
    (media_root / "2").mkdir(parents=True)
    # 放在 data/ 而非 data/media/ 下，任何路径穿越都会读到这个文件。
    (data_dir / "secret.key").write_bytes(b"TOP-SECRET-KEY")

    application = create_app(
        settings=Settings(_env_file=None, data_dir=data_dir), enable_startup=False
    )
    with TestClient(application) as client:
        yield client, media_root


def test_get_media_returns_png_bytes_with_declared_content_type(media_client) -> None:
    """正常取图：状态码、Content-Type 与文件字节都对得上。"""
    client, media_root = media_client
    (media_root / "1" / "1-1.png").write_bytes(PNG_BYTES)

    response = client.get("/api/v1/media/1/1-1.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == PNG_BYTES


def test_get_media_maps_jpg_suffix_to_jpeg_content_type(media_client) -> None:
    """jpg 后缀按 image/jpeg 返回。"""
    client, media_root = media_client
    (media_root / "1" / "1-2.jpg").write_bytes(JPG_BYTES)

    response = client.get("/api/v1/media/1/1-2.jpg")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == JPG_BYTES


@pytest.mark.parametrize(
    "file_name",
    ["../secret.key", "..", "../../data/secret.key", "/etc/passwd", ".secret.key"],
)
def test_resolve_media_path_rejects_traversal_and_absolute_names(
    media_client, file_name: str
) -> None:
    """服务层面对原始穿越串直接拒绝，不依赖路由层是否做过归一化。"""
    _client, media_root = media_client

    with pytest.raises(AppError) as excinfo:
        resolve_media_path(media_root, 1, file_name)

    assert excinfo.value.code is ErrorCode.MEDIA_NOT_FOUND


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/media/1/%2e%2e%2fsecret.key",
        "/api/v1/media/1/..%2Fsecret.key",
        "/api/v1/media/1/%2Fetc%2Fpasswd",
    ],
)
def test_get_media_never_serves_files_outside_paper_directory(
    media_client, url: str
) -> None:
    """编码过的穿越串和绝对路径都拿不到图片，也不会泄露密钥内容。"""
    client, _media_root = media_client

    response = client.get(url)

    assert response.status_code == 404
    assert b"TOP-SECRET-KEY" not in response.content


def test_get_media_does_not_reach_another_paper_directory(media_client) -> None:
    """卷 1 有同名文件时，用卷 2 取也必须 404。"""
    client, media_root = media_client
    (media_root / "1" / "1-1.png").write_bytes(PNG_BYTES)

    response = client.get("/api/v1/media/2/1-1.png")

    assert response.status_code == 404
    assert response.json() == {
        "code": "MEDIA_NOT_FOUND",
        "message": "图片不存在",
        "details": {},
    }


def test_get_media_rejects_unsupported_suffix(media_client) -> None:
    """白名单外的后缀即使文件存在也不给取。"""
    client, media_root = media_client
    (media_root / "1" / "x.gif").write_bytes(b"GIF89a")

    response = client.get("/api/v1/media/1/x.gif")

    assert response.status_code == 404
    assert response.json()["code"] == "MEDIA_NOT_FOUND"


def test_get_media_returns_unified_not_found_for_missing_file(media_client) -> None:
    """文件不存在时返回统一错误结构。"""
    client, _media_root = media_client

    response = client.get("/api/v1/media/1/missing.png")

    assert response.status_code == 404
    assert response.json() == {
        "code": "MEDIA_NOT_FOUND",
        "message": "图片不存在",
        "details": {},
    }
