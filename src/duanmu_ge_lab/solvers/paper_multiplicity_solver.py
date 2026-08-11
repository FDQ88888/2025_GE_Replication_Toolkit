"""Paper-specific root systems for Examples 3 and 5."""

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import brentq, least_squares

from duanmu_ge_lab.equilibrium.candidate import EmissionTaxEquilibriumCandidate
from duanmu_ge_lab.paper_examples import (
    build_paper_example_3_tax_economy,
    paper_example_3_allocations,
    paper_example_3_good_1_excess,
    paper_example_3_reduction_percent,
    paper_example_3_signed_l1_prices,
)
from duanmu_ge_lab.solvers.tax_solver import build_emission_tax_candidate


@dataclass(frozen=True, slots=True)
class PaperExample3Root:
    """One discovered scalar root and its full tax candidate."""

    eta: float
    table_goods_sum_tax_rate: float
    reduction_percent: float
    scalar_residual: float
    candidate: EmissionTaxEquilibriumCandidate


@dataclass(frozen=True, slots=True)
class PaperExample3TaxSolver:
    """Find all sign-changing roots of the Supplement's eta equation."""

    eta_min: float = 0.2
    eta_max: float = 3.0
    scan_points: int = 10000
    root_tolerance: float = 1e-13
    root_deduplication_tolerance: float = 1e-8

    def __post_init__(self) -> None:
        if not 0.0 < self.eta_min < self.eta_max:
            raise ValueError("Example 3 eta scan requires 0<min<max.")
        if self.scan_points < 3:
            raise ValueError("Example 3 eta scan needs at least three points.")
        if not np.isfinite(self.root_tolerance) or self.root_tolerance <= 0.0:
            raise ValueError("Example 3 root tolerance must be positive.")
        if (
            not np.isfinite(self.root_deduplication_tolerance)
            or self.root_deduplication_tolerance <= 0.0
        ):
            raise ValueError("Example 3 root deduplication tolerance must be positive.")

    def solve_tax_rate(self, table_tax_rate: float) -> list[PaperExample3Root]:
        tau = float(table_tax_rate)
        grid = np.linspace(self.eta_min, self.eta_max, self.scan_points)
        roots: list[float] = []
        previous_eta = float(grid[0])
        previous_value = paper_example_3_good_1_excess(tau, previous_eta)
        for eta_value in grid[1:]:
            eta = float(eta_value)
            value = paper_example_3_good_1_excess(tau, eta)
            if value == 0.0:
                root = eta
            elif previous_value * value < 0.0:
                root = float(
                    brentq(
                        lambda current: paper_example_3_good_1_excess(
                            tau, current
                        ),
                        previous_eta,
                        eta,
                        xtol=self.root_tolerance,
                        rtol=max(self.root_tolerance, 4.0 * np.finfo(float).eps),
                    )
                )
            else:
                root = None
            if root is not None and all(
                abs(root - old) > self.root_deduplication_tolerance
                for old in roots
            ):
                roots.append(root)
            previous_eta = eta
            previous_value = value
        return [
            self.build_root(tau, eta) for eta in sorted(roots, reverse=True)
        ]

    def build_root(self, table_tax_rate: float, eta: float) -> PaperExample3Root:
        economy = build_paper_example_3_tax_economy(table_tax_rate)
        prices = paper_example_3_signed_l1_prices(table_tax_rate, eta)
        allocations = paper_example_3_allocations(table_tax_rate, eta)
        plans = np.empty((0, 3), dtype=float)
        residual = paper_example_3_good_1_excess(table_tax_rate, eta)
        candidate = build_emission_tax_candidate(
            economy,
            prices,
            allocations,
            plans,
            solver_success=True,
            solver_message="Brent root of Supplement Section 3.3 commodity-1 excess demand",
            solver_method="scan_plus_brentq:paper_example_3_eta",
            iterations=None,
            function_calls=None,
            metadata={
                "model_role": "PAPER_REPLICATION_EXAMPLE_3",
                "table_goods_sum_tax_rate": float(table_tax_rate),
                "eta_p1_over_p2": float(eta),
                "scalar_residual": float(residual),
            },
        )
        return PaperExample3Root(
            eta=float(eta),
            table_goods_sum_tax_rate=float(table_tax_rate),
            reduction_percent=paper_example_3_reduction_percent(
                table_tax_rate, eta
            ),
            scalar_residual=float(residual),
            candidate=candidate,
        )


@dataclass(frozen=True, slots=True)
class PaperExample5TargetSolver:
    """Solve market clearing and a target emissions reduction on each branch."""

    starts_eta_tau: Sequence[Sequence[float]]
    tolerance: float = 1e-13
    max_nfev: int = 3000
    residual_acceptance_tolerance: float = 1e-9
    root_deduplication_tolerance: float = 1e-7

    def __post_init__(self) -> None:
        for name in (
            "tolerance",
            "residual_acceptance_tolerance",
            "root_deduplication_tolerance",
        ):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value <= 0.0:
                raise ValueError(f"{name} must be finite and positive.")
        if self.max_nfev < 1:
            raise ValueError("max_nfev must be positive.")

    def solve_target_reduction(
        self, target_reduction_fraction: float
    ) -> list[PaperExample3Root]:
        target = float(target_reduction_fraction)
        if not 0.0 < target < 1.0:
            raise ValueError("Example 5 target reduction must lie in (0,1).")
        roots: list[tuple[float, float]] = []

        def equations(point: np.ndarray) -> np.ndarray:
            eta, tau = point
            return np.array(
                [
                    paper_example_3_good_1_excess(float(tau), float(eta)),
                    paper_example_3_reduction_percent(float(tau), float(eta))
                    / 100.0
                    - target,
                ]
            )

        for start in self.starts_eta_tau:
            result = least_squares(
                equations,
                np.asarray(start, dtype=float),
                bounds=(np.array([0.1, 0.0]), np.array([4.0, 0.04])),
                xtol=self.tolerance,
                ftol=self.tolerance,
                gtol=self.tolerance,
                max_nfev=self.max_nfev,
            )
            eta, tau = (float(value) for value in result.x)
            if (
                not result.success
                or float(np.max(np.abs(result.fun)))
                > self.residual_acceptance_tolerance
            ):
                continue
            if all(
                np.linalg.norm(np.array([eta, tau]) - old)
                > self.root_deduplication_tolerance
                for old in roots
            ):
                roots.append((eta, tau))
        example3_solver = PaperExample3TaxSolver()
        return [
            example3_solver.build_root(tau, eta)
            for eta, tau in sorted(roots, key=lambda pair: pair[1], reverse=True)
        ]
