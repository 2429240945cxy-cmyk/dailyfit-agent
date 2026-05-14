from __future__ import annotations

import re

PATTERNS: list[tuple[str, str, str]] = [
    (r"(不吃牛肉|不喜欢牛肉|牛肉过敏)", "preference", "用户不吃牛肉"),
    (r"(素食|vegetarian|vegan)", "preference", "用户偏好素食"),
    (r"(乳糖不耐|lactose intolerant)", "constraint", "用户乳糖不耐"),
    (r"(减脂|cutting|lose fat)", "goal", "用户目标是减脂"),
    (r"(增肌|bulk|gain muscle)", "goal", "用户目标是增肌"),
    (r"(马拉松|marathon)", "goal", "用户在准备马拉松"),
    (r"(膝盖疼|膝盖痛|knee pain)", "constraint", "用户有膝盖疼痛"),
    (r"(肩伤|shoulder injury)", "constraint", "用户有肩伤"),
    (r"(腰伤|lower back pain)", "constraint", "用户有腰伤或下背疼痛"),
    (r"(早餐.*简单|simple breakfast)", "preference", "用户喜欢简单早餐"),
    (r"(喜欢中餐|Chinese food)", "preference", "用户喜欢中餐"),
    (r"(预算低|low budget|省钱)", "constraint", "用户预算低"),
]


def distill_memories(message: str) -> list[dict]:
    memories = []
    for pattern, memory_type, summary in PATTERNS:
        if re.search(pattern, message, flags=re.IGNORECASE):
            memories.append(
                {"type": memory_type, "summary": summary, "retrievable_text": summary, "metadata": {}}
            )
    profile_bits = []
    age = re.search(r"(\d{2})\s*岁", message)
    height = re.search(r"(\d{3})\s*cm", message, flags=re.IGNORECASE)
    weight = re.search(r"(\d{2,3})\s*kg", message, flags=re.IGNORECASE)
    if age:
        profile_bits.append(f"{age.group(1)}岁")
    if "男" in message or "male" in message.lower():
        profile_bits.append("男性")
    if "女" in message or "female" in message.lower():
        profile_bits.append("女性")
    if height:
        profile_bits.append(f"身高{height.group(1)}cm")
    if weight:
        profile_bits.append(f"体重{weight.group(1)}kg")
    if profile_bits:
        summary = "，".join(profile_bits)
        memories.append(
            {
                "type": "profile",
                "summary": f"用户资料：{summary}",
                "retrievable_text": f"用户资料：{summary}",
                "metadata": {"profile": True},
            }
        )
    return memories
