from __future__ import annotations

import re

PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"不吃牛肉|不喜欢牛肉|牛肉过敏|戒(?:了)?牛肉|不沾牛肉|吃不了红肉|red meat.{0,8}(no|allergy|avoid)", re.I), "constraint", "用户不吃牛肉"),
    (re.compile(r"素食|vegetarian|vegan|不吃肉|不沾肉|戒肉", re.I), "preference", "用户偏好素食"),
    (re.compile(r"乳糖不耐|lactose intolerant|喝奶拉肚|不喝牛奶|喝奶不舒服|milk-free", re.I), "constraint", "用户乳糖不耐"),
    (re.compile(r"麸质过敏|gluten.{0,8}(allergy|intolerant|free)|不吃面筋", re.I), "constraint", "用户麸质过敏"),
    (re.compile(r"海鲜过敏|shellfish allergy|不吃海鲜", re.I), "constraint", "用户海鲜过敏"),
    (re.compile(r"花生过敏|peanut allergy|坚果过敏|nut allergy", re.I), "constraint", "用户坚果/花生过敏"),
    (re.compile(r"喜欢中餐|中餐|Chinese (food|cuisine)|爱吃中国菜", re.I), "preference", "用户喜欢中餐"),
    (re.compile(r"喜欢日料|Japanese (food|cuisine)|爱吃日本菜", re.I), "preference", "用户喜欢日料"),
    (re.compile(r"预算低|low budget|省钱|便宜点|预算.*紧|cheap meals", re.I), "constraint", "用户预算低"),
    (re.compile(r"早餐.{0,8}简单|简单(?:点)?的?早餐|快手.*早餐|quick breakfast|simple breakfast", re.I), "preference", "用户喜欢简单早餐"),
    (re.compile(r"减脂|cutting|lose fat|想瘦|减重|降体脂|减肥", re.I), "goal", "用户目标是减脂"),
    (re.compile(r"增肌|bulk|gain muscle|长肌肉|想壮|增重", re.I), "goal", "用户目标是增肌"),
    (re.compile(r"维持(?:体重|目前)|maintenance|保持体重", re.I), "goal", "用户目标是维持"),
    (re.compile(r"塑形|recomposition|body recomp|增肌减脂", re.I), "goal", "用户目标是塑形/recomp"),
    (re.compile(r"准备马拉松|马拉松训练|marathon training|要跑马拉松|长跑", re.I), "goal", "用户在准备马拉松"),
    (re.compile(r"膝盖.{0,6}(疼|痛|不适|有问题|受伤|半月板)|knee (pain|injury|issue)", re.I), "constraint", "用户有膝盖疼痛"),
    (re.compile(r"肩.{0,6}(疼|痛|伤|不适|脱臼)|shoulder (pain|injury|impingement)", re.I), "constraint", "用户有肩伤"),
    (re.compile(r"腰.{0,4}(疼|痛|伤|不适)|背.{0,4}(疼|痛|伤)|lower back (pain|injury)", re.I), "constraint", "用户有腰伤或下背疼痛"),
    (re.compile(r"手腕.{0,4}(疼|痛|伤)|wrist (pain|injury)", re.I), "constraint", "用户有手腕问题"),
    (re.compile(r"脚踝.{0,4}(疼|痛|扭|伤)|ankle (pain|sprain|injury)", re.I), "constraint", "用户有脚踝问题"),
    (re.compile(r"糖尿病|diabetes|血糖问题", re.I), "constraint", "用户有糖尿病"),
    (re.compile(r"高血压|hypertension|血压高", re.I), "constraint", "用户有高血压"),
    (re.compile(r"孕期|怀孕|pregnant|pregnancy", re.I), "constraint", "用户处于孕期"),
    (re.compile(r"哺乳|breastfeeding|nursing", re.I), "constraint", "用户处于哺乳期"),
    (re.compile(r"在家(?:训)?练|home (workout|training)|没有器械|徒手", re.I), "preference", "用户在家训练/徒手"),
    (re.compile(r"健身房|gym|去健身房", re.I), "preference", "用户在健身房训练"),
    (re.compile(r"只有哑铃|dumbbell only|哑铃为主", re.I), "preference", "用户主要使用哑铃"),
]


def distill_memories(message: str) -> list[dict]:
    memories = []
    seen_summaries = set()
    for pattern, memory_type, summary in PATTERNS:
        if pattern.search(message):
            if summary in seen_summaries:
                continue
            seen_summaries.add(summary)
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
