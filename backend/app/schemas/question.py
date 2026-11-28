from pydantic import BaseModel


class Answer(BaseModel):
    """答案与解析的唯一出口，字段顺序即接口返回顺序。"""

    # 客观题的选项数组，主观题为 null；数组顺序保持入库时的原样，不做排序。
    answer_choice: list[str] | None
    # 主观题的参考答案文本，客观题为 null。
    answer_text: str | None
    # 解析按 Markdown 原文返回，不在服务端渲染。
    analysis: str | None
    # 知识点标签，没有标签时是空数组而不是 null。
    knowledge_tags: list[str]
