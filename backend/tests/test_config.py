from pathlib import Path

from app.config import REPOSITORY_ROOT, Settings


def test_settings_can_be_overridden_by_environment(monkeypatch) -> None:
    """验证环境变量可以覆盖默认服务端口。"""
    monkeypatch.setenv("APP_PORT", "9000")

    settings = Settings(_env_file=None)

    assert settings.port == 9000


def test_settings_can_be_overridden_by_dotenv(tmp_path) -> None:
    """验证 dotenv 文件中的配置可以覆盖默认服务端口。"""
    env_file = tmp_path / ".env"
    env_file.write_text("APP_PORT=9100\n", encoding="utf-8")

    settings = Settings(_env_file=env_file)

    assert settings.port == 9100


def test_data_dir_defaults_to_repository_data_directory(monkeypatch) -> None:
    """验证数据目录默认指向仓库根目录下的 data。"""
    monkeypatch.delenv("APP_DATA_DIR", raising=False)

    settings = Settings(_env_file=None)

    assert settings.data_dir == REPOSITORY_ROOT / "data"
    assert settings.data_dir == Path(REPOSITORY_ROOT / "data")
