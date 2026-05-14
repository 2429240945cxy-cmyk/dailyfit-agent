from __future__ import annotations

from pydantic import BaseModel

from backend.runtime.config import get_settings
from backend.runtime.llm_usage import UsageStore


class BudgetStatus(BaseModel):
    budget_exceeded: bool
    daily_budget_usd: float
    spent_today_usd: float
    mode_switch: str | None = None


class BudgetManager:
    def __init__(self, usage_store: UsageStore | None = None) -> None:
        self.settings = get_settings()
        self.usage_store = usage_store or UsageStore()

    def check(self) -> BudgetStatus:
        spent = self.usage_store.spent_today()
        exceeded = spent >= self.settings.budget_usd
        return BudgetStatus(
            budget_exceeded=exceeded,
            daily_budget_usd=self.settings.budget_usd,
            spent_today_usd=round(spent, 6),
            mode_switch="live_to_mock_budget_exceeded" if exceeded else None,
        )
