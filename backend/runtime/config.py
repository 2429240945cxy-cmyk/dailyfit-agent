from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    mode: str
    db_path: Path
    audit_dir: Path
    cache_dir: Path
    dashscope_api_key_present: bool
    dashscope_base_url: str
    llm_provider: str
    llm_model: str
    judge_provider: str
    judge_model: str
    embedding_provider: str
    embedding_model: str
    embedding_dim: int
    usda_api_key_present: bool
    budget_usd: float
    github_mode: str
    github_repo_name: str
    allow_network: bool

    @property
    def public_mode(self) -> str:
        if self.mode == "demo_mock":
            return "demo_mock"
        if self.mode == "live":
            return "live_real" if self.dashscope_api_key_present else "live_missing_key_not_run"
        return self.mode


def project_path(value: str | os.PathLike[str]) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT_DIR / path


def get_settings() -> Settings:
    mode = os.getenv("DAILYFIT_MODE", "demo_mock")
    return Settings(
        mode=mode,
        db_path=project_path(os.getenv("DAILYFIT_DB_PATH", "dailyfit.db")),
        audit_dir=project_path(os.getenv("DAILYFIT_AUDIT_DIR", "data/audits")),
        cache_dir=project_path(os.getenv("DAILYFIT_CACHE_DIR", "data/cache")),
        dashscope_api_key_present=bool(os.getenv("DASHSCOPE_API_KEY")),
        dashscope_base_url=os.getenv(
            "DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ),
        llm_provider=os.getenv("DAILYFIT_LLM_PROVIDER", "aliyun_openai"),
        llm_model=os.getenv("DAILYFIT_LLM_MODEL", "qwen-plus"),
        judge_provider=os.getenv("DAILYFIT_JUDGE_PROVIDER", "aliyun_openai"),
        judge_model=os.getenv("DAILYFIT_JUDGE_MODEL", "qwen-max"),
        embedding_provider=os.getenv("DAILYFIT_EMBEDDING_PROVIDER", "aliyun_openai"),
        embedding_model=os.getenv("DAILYFIT_EMBEDDING_MODEL", "text-embedding-v4"),
        embedding_dim=int(os.getenv("DAILYFIT_EMBEDDING_DIM", "1024")),
        usda_api_key_present=bool(os.getenv("USDA_API_KEY")),
        budget_usd=float(os.getenv("DAILYFIT_BUDGET_USD", "1.00")),
        github_mode=os.getenv("DAILYFIT_GITHUB_MODE", "auto"),
        github_repo_name=os.getenv("GITHUB_REPO_NAME", "dailyfit-agent"),
        allow_network=_bool_env("DAILYFIT_ALLOW_NETWORK", True),
    )
