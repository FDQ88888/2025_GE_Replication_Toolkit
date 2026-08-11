"""Explicit consumer-income accounting shared by production and policy layers."""

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True, slots=True)
class IncomeBreakdown:
    """Decompose the budget income used by a consumer optimization problem.

    Negative firm profit is passed through to owners without a hidden limited-
    liability rule. ``policy_income`` is zero in Milestone 2 and reserved as an
    explicit coordinate for later paper-defined policies.
    """

    endowment_income: float
    firm_dividend_income: float = 0.0
    policy_income: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.endowment_income,
            self.firm_dividend_income,
            self.policy_income,
        )
        if not all(np.isfinite(value) for value in values):
            raise ValueError("Every income component must be finite.")

    @property
    def total_income(self) -> float:
        """Return the exact sum of all named income components."""

        return float(
            self.endowment_income
            + self.firm_dividend_income
            + self.policy_income
        )

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-serializable accounting data."""

        return {
            "endowment_income": self.endowment_income,
            "firm_dividend_income": self.firm_dividend_income,
            "policy_income": self.policy_income,
            "total_income": self.total_income,
        }
