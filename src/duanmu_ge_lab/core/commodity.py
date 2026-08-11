"""Commodity metadata and explicit market-clearing rules."""

from dataclasses import dataclass
from enum import Enum


class ClearingRule(str, Enum):
    """Rule imposed on a commodity's aggregate excess demand."""

    EXACT = "exact"
    FREE_DISPOSAL = "free_disposal"


class CommodityKind(str, Enum):
    """Semantic commodity label that carries no automatic mathematical restriction."""

    GOOD = "good"
    BAD = "bad"


@dataclass(frozen=True, slots=True)
class Commodity:
    """Describe one commodity in a finite economy.

    Economic interpretation
        A commodity is an indexed accounting coordinate. Its semantic kind does not
        determine price signs, preferences, regulation, or disposal.
    Mathematical definition
        ``clearing_rule=EXACT`` requires zero aggregate excess demand.
        ``FREE_DISPOSAL`` permits nonpositive aggregate excess demand.
    Parameters
        name: Human-readable commodity name.
        index: Zero-based coordinate in every economic vector.
        clearing_rule: Explicit resource-clearing convention.
        kind: Semantic label only.
    Raises
        ValueError: If the name is empty or the index is negative.
        TypeError: If enum-valued fields are not valid enum members.
    """

    name: str
    index: int
    clearing_rule: ClearingRule = ClearingRule.EXACT
    kind: CommodityKind = CommodityKind.GOOD

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Commodity name must be non-empty.")
        if self.index < 0:
            raise ValueError("Commodity index must be nonnegative.")
        if not isinstance(self.clearing_rule, ClearingRule):
            raise TypeError("clearing_rule must be a ClearingRule.")
        if not isinstance(self.kind, CommodityKind):
            raise TypeError("kind must be a CommodityKind.")

