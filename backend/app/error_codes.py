from enum import StrEnum


class ErrorCode(StrEnum):
    """业务与框架错误码的集中注册表。"""

    # 请求的试卷不存在。
    PAPER_NOT_FOUND = "PAPER_NOT_FOUND"
    # 题目/试卷引用的媒体资源（如插图）不存在。
    MEDIA_NOT_FOUND = "MEDIA_NOT_FOUND"
    # 请求的题目不存在。
    QUESTION_NOT_FOUND = "QUESTION_NOT_FOUND"
    # 题目已在错题本中，重复加入。
    ALREADY_IN_WRONGBOOK = "ALREADY_IN_WRONGBOOK"
    # 题目不在错题本中，却执行了移除等操作。
    NOT_IN_WRONGBOOK = "NOT_IN_WRONGBOOK"
    # 作答选择非法：越出选项范围或与题型不符。
    INVALID_CHOICE = "INVALID_CHOICE"
    # 设置的考试时长非法（如 <= 0）。
    INVALID_DURATION = "INVALID_DURATION"
    # 对已交卷/结束的考试执行了作答、继续考试等操作。
    EXAM_FINISHED = "EXAM_FINISHED"
    # 主观题自评分非法（负数或超出本题分值）。
    INVALID_SELF_SCORE = "INVALID_SELF_SCORE"
    # 上传的文件类型不受支持（仅 pdf/png/jpg/webp）。
    FILE_TYPE_UNSUPPORTED = "FILE_TYPE_UNSUPPORTED"
    # 上传文件超过大小限制。
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    # 试卷标题非法（空或超长）。
    INVALID_TITLE = "INVALID_TITLE"
    # 试卷年份非法。
    INVALID_YEAR = "INVALID_YEAR"
    # 导入任务不存在。
    IMPORT_NOT_FOUND = "IMPORT_NOT_FOUND"
    # 题目内容校验不通过。
    INVALID_QUESTION = "INVALID_QUESTION"
    # 题目缺少必填信息（如答案、分值），不能审核入库。
    QUESTION_INCOMPLETE = "QUESTION_INCOMPLETE"
    # 同一张卷内题号重复。
    SEQ_NO_DUPLICATED = "SEQ_NO_DUPLICATED"
    # 对已审核通过的题目执行了修改。
    QUESTION_REVIEWED = "QUESTION_REVIEWED"
    # 导入任务当前状态不允许重试。
    IMPORT_NOT_RETRYABLE = "IMPORT_NOT_RETRYABLE"
    # 导入任务已完成，不能重复操作。
    IMPORT_COMPLETED = "IMPORT_COMPLETED"
    # 调用模型前发现 OpenAI 兼容接口未配置。
    LLM_NOT_CONFIGURED = "LLM_NOT_CONFIGURED"
    # 请求参数校验失败（框架级，方案校验错误时抛出）。
    VALIDATION_ERROR = "VALIDATION_ERROR"
    # 未处理的内部异常（框架级，兜底返回 500）。
    INTERNAL_ERROR = "INTERNAL_ERROR"
    # 框架 HTTP 异常的统一包装码（非业务错误清单成员）。
    HTTP_ERROR = "HTTP_ERROR"


ERROR_STATUS: dict[ErrorCode, int] = {
    # 业务错误码的状态码与 docs/03-接口文档.md 第 11 章保持一一对应。
    ErrorCode.PAPER_NOT_FOUND: 404,
    ErrorCode.MEDIA_NOT_FOUND: 404,
    ErrorCode.QUESTION_NOT_FOUND: 404,
    ErrorCode.ALREADY_IN_WRONGBOOK: 409,
    ErrorCode.NOT_IN_WRONGBOOK: 400,
    ErrorCode.INVALID_CHOICE: 400,
    ErrorCode.INVALID_DURATION: 400,
    ErrorCode.EXAM_FINISHED: 409,
    ErrorCode.INVALID_SELF_SCORE: 400,
    ErrorCode.FILE_TYPE_UNSUPPORTED: 400,
    ErrorCode.FILE_TOO_LARGE: 400,
    ErrorCode.INVALID_TITLE: 400,
    ErrorCode.INVALID_YEAR: 400,
    ErrorCode.IMPORT_NOT_FOUND: 404,
    ErrorCode.INVALID_QUESTION: 400,
    ErrorCode.QUESTION_INCOMPLETE: 400,
    ErrorCode.SEQ_NO_DUPLICATED: 400,
    ErrorCode.QUESTION_REVIEWED: 409,
    ErrorCode.IMPORT_NOT_RETRYABLE: 409,
    ErrorCode.IMPORT_COMPLETED: 409,
    ErrorCode.LLM_NOT_CONFIGURED: 400,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.INTERNAL_ERROR: 500,
    # HTTP_ERROR 仅供框架异常包装使用，不属于业务错误清单。
    ErrorCode.HTTP_ERROR: 500,
}

BUSINESS_ERROR_CODES = frozenset(
    code for code in ErrorCode if code is not ErrorCode.HTTP_ERROR
)


def status_for(code: ErrorCode) -> int:
    """返回已注册错误码对应的 HTTP 状态码。"""
    try:
        return ERROR_STATUS[code]
    except KeyError as exc:  # pragma: no cover - 防止未来漏注册
        raise RuntimeError(f"Error code has no HTTP status: {code}") from exc