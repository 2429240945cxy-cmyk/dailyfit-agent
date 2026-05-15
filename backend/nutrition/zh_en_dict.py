"""Chinese-to-English food name translation for nutrition DB lookup."""

from __future__ import annotations

FOOD_ZH_EN: dict[str, str] = {
    "燕麦": "oats rolled raw",
    "燕麦片": "oats rolled raw",
    "白米饭": "rice white cooked",
    "米饭": "rice white cooked",
    "糙米": "rice brown cooked",
    "糙米饭": "rice brown cooked",
    "全麦面包": "bread whole wheat",
    "白面包": "bread white",
    "面包": "bread white",
    "意大利面": "pasta cooked",
    "意面": "pasta cooked",
    "藜麦": "quinoa cooked",
    "红薯": "sweet potato baked",
    "土豆": "potato baked",
    "玉米": "corn sweet yellow cooked",
    "鸡胸肉": "chicken breast roasted",
    "鸡胸": "chicken breast roasted",
    "鸡腿": "chicken thigh roasted",
    "鸡蛋": "egg whole boiled",
    "蛋白": "egg white",
    "三文鱼": "salmon atlantic cooked",
    "鲑鱼": "salmon atlantic cooked",
    "金枪鱼": "tuna canned water",
    "鳕鱼": "cod cooked",
    "虾": "shrimp cooked",
    "牛肉": "beef ground lean cooked",
    "瘦牛肉": "beef ground 90 lean cooked",
    "猪肉": "pork loin lean cooked",
    "瘦猪肉": "pork loin lean cooked",
    "羊肉": "lamb cooked",
    "豆腐": "tofu firm",
    "嫩豆腐": "tofu soft",
    "豆浆": "soymilk unsweetened",
    "希腊酸奶": "yogurt greek plain nonfat",
    "酸奶": "yogurt plain whole",
    "西兰花": "broccoli raw",
    "花椰菜": "cauliflower raw",
    "菠菜": "spinach raw",
    "胡萝卜": "carrot raw",
    "番茄": "tomato red raw",
    "西红柿": "tomato red raw",
    "黄瓜": "cucumber raw",
    "生菜": "lettuce romaine raw",
    "白菜": "cabbage chinese raw",
    "卷心菜": "cabbage raw",
    "茄子": "eggplant raw",
    "青椒": "pepper sweet green raw",
    "彩椒": "pepper sweet red raw",
    "蘑菇": "mushrooms white raw",
    "洋葱": "onion raw",
    "苹果": "apple raw with skin",
    "香蕉": "banana raw",
    "橙子": "orange raw",
    "葡萄": "grapes raw",
    "蓝莓": "blueberries raw",
    "草莓": "strawberries raw",
    "牛油果": "avocado raw",
    "鳄梨": "avocado raw",
    "西瓜": "watermelon raw",
    "菠萝": "pineapple raw",
    "牛奶": "milk whole",
    "全脂牛奶": "milk whole",
    "脱脂牛奶": "milk nonfat",
    "奶酪": "cheese cheddar",
    "黄油": "butter without salt",
    "杏仁": "almonds raw",
    "核桃": "walnuts english",
    "腰果": "cashew nuts raw",
    "花生": "peanuts raw",
    "花生酱": "peanut butter smooth",
    "葵花籽": "sunflower seeds dried",
    "南瓜籽": "pumpkin seeds dried",
    "芝麻": "sesame seeds whole roasted",
    "黑巧克力": "chocolate dark 70 85",
    "巧克力": "chocolate milk",
    "蛋白粉": "whey protein powder",
    "燕麦奶": "oat milk unsweetened",
    "杏仁奶": "almond milk unsweetened",
    "蜂蜜": "honey",
    "橄榄油": "oil olive",
    "椰子油": "oil coconut",
    "酱油": "soy sauce",
    "醋": "vinegar",
}


def translate_food_query(query: str) -> tuple[str, bool, str]:
    """Return translated query, translation flag, and matched Chinese key."""
    if not query:
        return query, False, ""

    query_clean = query.strip()
    if query_clean in FOOD_ZH_EN:
        return FOOD_ZH_EN[query_clean], True, query_clean

    matches = [(zh, en) for zh, en in FOOD_ZH_EN.items() if zh in query_clean]
    if matches:
        zh, en = max(matches, key=lambda pair: len(pair[0]))
        return en, True, zh

    return query_clean, False, ""
