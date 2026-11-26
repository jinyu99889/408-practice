import re
from pathlib import Path

import pytest

from app.error_codes import BUSINESS_ERROR_CODES, ERROR_STATUS, ErrorCode


def test_every_registered_error_code_has_status() -> None:
    assert set(ERROR_STATUS) == set(ErrorCode)
    assert all(isinstance(status, int) and status >= 400 for status in ERROR_STATUS.values())


def test_business_registry_matches_interface_document() -> None:
    document_path = Path(__file__).resolve().parents[2] / "docs" / "03-接口文档.md"
    if not document_path.exists():
        pytest.skip("本地 docs/ 未纳入 CI checkout，跳过文档同步检查")

    document = document_path.read_text(encoding="utf-8")
    documented = {
        code: int(status)
        for code, status in re.findall(r"\| ([A-Z][A-Z0-9_]+) \| ([0-9]+) \|", document)
    }
    assert {code.value for code in BUSINESS_ERROR_CODES} == set(documented)
    assert {
        code.value: status
        for code, status in ERROR_STATUS.items()
        if code in BUSINESS_ERROR_CODES
    } == documented
