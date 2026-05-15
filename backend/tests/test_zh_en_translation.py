from backend.nutrition.zh_en_dict import translate_food_query


def test_exact_match() -> None:
    en, was_translated, key = translate_food_query("燕麦")
    assert was_translated
    assert "oats" in en
    assert key == "燕麦"


def test_substring_match() -> None:
    en, was_translated, key = translate_food_query("一份燕麦片")
    assert was_translated
    assert "oats" in en
    assert key == "燕麦片"


def test_longest_match() -> None:
    en, was_translated, key = translate_food_query("全麦面包")
    assert was_translated
    assert "whole wheat" in en
    assert key == "全麦面包"


def test_no_match() -> None:
    en, was_translated, key = translate_food_query("xxxx unknown food")
    assert not was_translated
    assert en == "xxxx unknown food"
    assert key == ""


def test_english_passthrough() -> None:
    en, was_translated, key = translate_food_query("chicken breast")
    assert not was_translated
    assert en == "chicken breast"
    assert key == ""
