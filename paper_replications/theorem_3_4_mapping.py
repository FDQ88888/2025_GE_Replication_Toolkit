"""Numerically check the paper's quota-tax mappings on Example 1."""

from pathlib import Path
from typing import Any

import numpy as np

from duanmu_ge_lab import (
    EmissionTaxEconomy,
    EmissionTaxEquilibriumDiagnostics,
    EmissionTaxPolicy,
    FixedNumeraire,
    PaperExample1QuotaSolver,
    PaperTaxConvention,
    PriceSign,
    PriceSignRestrictions,
    QuotaEquilibriumDiagnostics,
    build_emission_tax_candidate,
    build_paper_example_1,
    build_quota_candidate,
    map_emission_tax_to_global_quota,
    map_quota_to_emission_tax,
)

from paper_replications.common import compare_numeric, load_yaml_mapping, write_json

ROOT = Path(__file__).resolve().parents[1]
PRICE_SIGNS = PriceSignRestrictions(
    (PriceSign.NEGATIVE, PriceSign.POSITIVE, PriceSign.POSITIVE)
)


def run(config_path: Path | None = None) -> dict[str, Any]:
    config_file = config_path or ROOT / "configs" / "paper" / "theorem_3_4_mapping.yaml"
    config = load_yaml_mapping(config_file)
    v = float(config["model"]["emissions_quota_v"])
    comparison = config["comparison"]
    compare_kwargs = {
        "absolute_tolerance": float(comparison["absolute_tolerance"]),
        "relative_tolerance": float(comparison["relative_tolerance"]),
    }

    quota_economy, _ = build_paper_example_1(v)
    quota_candidate = PaperExample1QuotaSolver().solve(quota_economy)
    quota_report = QuotaEquilibriumDiagnostics(
        quota_economy, price_sign_restrictions=PRICE_SIGNS
    ).evaluate(quota_candidate)

    tax_economy = map_quota_to_emission_tax(
        quota_economy, quota_candidate.prices
    )
    tax_candidate = build_emission_tax_candidate(
        tax_economy,
        np.asarray(quota_candidate.prices),
        np.asarray(quota_candidate.allocations),
        np.asarray(quota_candidate.firm_plans)[1:],
        solver_success=True,
        solver_message="Mapped from verified quota candidate under Theorem 3",
        solver_method="paper_theorem_3_mapping",
        iterations=0,
        function_calls=0,
        metadata={
            "claim_scope": "NUMERICAL CHECK OF THEORETICAL MAPPING",
            "source": "paper Example 1 quota candidate",
        },
    )
    tax_report = EmissionTaxEquilibriumDiagnostics(
        tax_economy, price_sign_restrictions=PRICE_SIGNS
    ).evaluate(tax_candidate)

    reverse_quota_economy = map_emission_tax_to_global_quota(
        tax_economy, tax_candidate.allocations, tax_candidate.firm_plans
    )
    reverse_plans = np.vstack(
        [np.zeros(tax_economy.n_goods), np.asarray(tax_candidate.firm_plans)]
    )
    reverse_candidate = build_quota_candidate(
        reverse_quota_economy,
        np.asarray(tax_candidate.prices),
        np.asarray(tax_candidate.allocations),
        reverse_plans,
        solver_success=True,
        solver_message="Mapped from verified tax candidate under Theorem 4",
        solver_method="paper_theorem_4_mapping",
        iterations=0,
        function_calls=0,
        metadata={
            "claim_scope": "NUMERICAL CHECK OF THEORETICAL MAPPING",
            "source": "mapped emission-tax candidate",
        },
    )
    reverse_report = QuotaEquilibriumDiagnostics(
        reverse_quota_economy, price_sign_restrictions=PRICE_SIGNS
    ).evaluate(reverse_candidate)

    direct_checks = {
        "prices": compare_numeric(
            quota_candidate.prices, tax_candidate.prices, **compare_kwargs
        ),
        "allocations": compare_numeric(
            quota_candidate.allocations, tax_candidate.allocations, **compare_kwargs
        ),
        "private_firm_plans": compare_numeric(
            np.asarray(quota_candidate.firm_plans)[1:],
            tax_candidate.firm_plans,
            **compare_kwargs,
        ),
        "consumer_incomes": compare_numeric(
            quota_candidate.income_breakdowns,
            tax_candidate.income_breakdowns,
            **compare_kwargs,
        ),
        "theorem_3_rebate_shares": compare_numeric(
            {"omega_1": 0.0, "omega_2": 1.0},
            dict(tax_economy.policy.rebate_shares),
            **compare_kwargs,
        ),
        "reverse_total_m": compare_numeric(
            quota_economy.policy.total_m,
            reverse_quota_economy.policy.total_m,
            **compare_kwargs,
        ),
    }

    numeraire = FixedNumeraire(
        index=int(config["coordinates"]["internal_numeraire_index"]),
        value=float(config["coordinates"]["internal_numeraire_value"]),
    )
    conversion = PaperTaxConvention.to_fixed_numeraire(
        tax_candidate.prices, tax_economy.policy.tax_rates, numeraire
    )
    roundtrip = PaperTaxConvention.to_paper_l1(
        conversion.prices, conversion.tax_rates
    )
    scaled_policy = EmissionTaxPolicy(
        regulated_count=tax_economy.policy.regulated_count,
        tax_rates=conversion.tax_rates,
        rebate_shares=tax_economy.policy.rebate_shares,
        unregulated_rules=tax_economy.policy.unregulated_rules,
    )
    scaled_economy = EmissionTaxEconomy(
        tax_economy.production_economy, scaled_policy
    )
    paper_incomes = tax_economy.income_breakdowns(
        tax_candidate.prices, tax_candidate.allocations, tax_candidate.firm_plans
    )
    scaled_incomes = scaled_economy.income_breakdowns(
        conversion.prices, tax_candidate.allocations, tax_candidate.firm_plans
    )
    paper_profits = tax_economy.firm_profits(
        tax_candidate.prices, tax_candidate.firm_plans
    )
    scaled_profits = scaled_economy.firm_profits(
        conversion.prices, tax_candidate.firm_plans
    )
    paper_demands = tax_economy.individual_demands(
        tax_candidate.prices, tax_candidate.allocations, tax_candidate.firm_plans
    )
    scaled_demands = scaled_economy.individual_demands(
        conversion.prices, tax_candidate.allocations, tax_candidate.firm_plans
    )
    scale = conversion.scale
    coordinate_checks = {
        "paper_price_roundtrip": compare_numeric(
            tax_candidate.prices, roundtrip.prices, **compare_kwargs
        ),
        "paper_tax_roundtrip": compare_numeric(
            tax_economy.policy.tax_rates, roundtrip.tax_rates, **compare_kwargs
        ),
        "demand_quantities_invariant": compare_numeric(
            paper_demands, scaled_demands, **compare_kwargs
        ),
        "firm_profits_scale_adjusted": compare_numeric(
            paper_profits, scaled_profits / scale, **compare_kwargs
        ),
        "tax_revenue_scale_adjusted": compare_numeric(
            tax_economy.tax_revenue(
                tax_candidate.allocations, tax_candidate.firm_plans
            ),
            scaled_economy.tax_revenue(
                tax_candidate.allocations, tax_candidate.firm_plans
            )
            / scale,
            **compare_kwargs,
        ),
        "consumer_incomes_scale_adjusted": compare_numeric(
            {key: value.total_income for key, value in paper_incomes.items()},
            {
                key: value.total_income / scale
                for key, value in scaled_incomes.items()
            },
            **compare_kwargs,
        ),
    }
    all_checks = [*direct_checks.values(), *coordinate_checks.values()]
    success = bool(
        quota_report.passed
        and tax_report.passed
        and reverse_report.passed
        and all(item["passed"] for item in all_checks)
    )
    result = {
        "status": (
            "NUMERICAL_MAPPING_CHECK_SUCCESS"
            if success
            else "NUMERICAL_MAPPING_CHECK_FAILURE"
        ),
        "claim_scope": "NUMERICAL CHECK OF THEORETICAL MAPPING; NOT A PROOF",
        "paper": config["paper"],
        "source_quota_diagnostics": quota_report.to_dict(),
        "theorem_3_tax_candidate": tax_candidate.to_dict(),
        "theorem_3_tax_diagnostics": tax_report.to_dict(),
        "theorem_4_reverse_quota_candidate": reverse_candidate.to_dict(),
        "theorem_4_reverse_quota_diagnostics": reverse_report.to_dict(),
        "mapping_comparisons": direct_checks,
        "coordinate_conversion": {
            "paper_to_internal": conversion.to_dict(),
            "internal_to_paper": roundtrip.to_dict(),
            "checks": coordinate_checks,
        },
    }
    result["config_snapshot"] = config
    write_json(ROOT / "results" / "milestone6_theorem_3_4_mapping.json", result)
    return result


if __name__ == "__main__":
    output = run()
    print(output["status"])
    print(output["theorem_3_tax_diagnostics"]["classification"])
    print(output["theorem_4_reverse_quota_diagnostics"]["classification"])
