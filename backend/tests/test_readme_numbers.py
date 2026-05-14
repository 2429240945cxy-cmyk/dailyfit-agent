from pathlib import Path


def test_readme_has_benchmark_markers() -> None:
    text = Path("README.md").read_text(encoding="utf-8")
    assert "<!-- BENCHMARK_TABLE_START -->" in text
    assert "<!-- BENCHMARK_TABLE_END -->" in text
    assert "DailyFit Agent" in text
