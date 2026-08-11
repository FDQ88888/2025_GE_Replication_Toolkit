"""Generate research figures directly from persisted, verified experiment JSON."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from duanmu_ge_lab.experiment_io import write_json

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"

COLORS = ("#176B87", "#C44536", "#D39B2A", "#4C956C")


def _load(name: str) -> dict:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _finish(figure, filename: str, caption: str, source: str) -> None:
    figure.tight_layout()
    figure.savefig(
        FIGURES / filename,
        dpi=180,
        bbox_inches="tight",
        metadata={"Description": caption, "Source": source},
    )
    plt.close(figure)


def _tax_emission_correspondence(data: dict) -> dict:
    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    rows = data["tax_emissions_correspondence"]
    branch_ids = sorted(
        {item["equilibrium_id"] for row in rows for item in row["equilibria"]}
    )
    for branch_id in branch_ids:
        points = [
            (row["table_goods_sum_tax_rate"], item["emissions"])
            for row in rows
            for item in row["equilibria"]
            if item["equilibrium_id"] == branch_id
        ]
        if points:
            axis.plot(
                *zip(*points),
                marker="o",
                linewidth=1.3,
                color=COLORS[branch_id % len(COLORS)],
                label=f"Discovered branch {branch_id + 1}",
            )
    axis.set_xlabel("Emission tax rate (paper goods-sum convention)")
    axis.set_ylabel("Equilibrium emissions")
    axis.set_title("Tax Rate to Set of Verified Equilibrium Emissions")
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    caption = (
        "Every marker is a separately verified candidate from the Milestone 9 "
        "continuation plus fresh-multistart sweep; no branch averaging is used."
    )
    _finish(
        figure,
        "tax_emission_correspondence.png",
        caption,
        "results/milestone9_tax_quota_sweeps.json",
    )
    return {"caption": caption, "source": "results/milestone9_tax_quota_sweeps.json"}


def _quota_price_correspondence(data: dict) -> dict:
    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    rows = data["quota_price_correspondence"]
    branch_ids = sorted(
        {item["equilibrium_id"] for row in rows for item in row["equilibria"]}
    )
    for branch_id in branch_ids:
        points = [
            (
                100.0 * row["target_reduction_fraction"],
                item["quota_price_goods_sum_convention"],
            )
            for row in rows
            for item in row["equilibria"]
            if item["equilibrium_id"] == branch_id
        ]
        if points:
            axis.plot(
                *zip(*points),
                marker="s",
                linewidth=1.3,
                color=COLORS[branch_id % len(COLORS)],
                label=f"Discovered branch {branch_id + 1}",
            )
    axis.set_xlabel("Required emissions reduction (%)")
    axis.set_ylabel("Quota price (paper goods-sum convention)")
    axis.set_title("Quota Target to Set of Verified Quota Prices")
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    caption = (
        "Each target retains all verified quota-price clusters found in Milestone 9; "
        "the plot does not assert that the discovered set is exhaustive."
    )
    _finish(
        figure,
        "quota_price_correspondence.png",
        caption,
        "results/milestone9_tax_quota_sweeps.json",
    )
    return {"caption": caption, "source": "results/milestone9_tax_quota_sweeps.json"}


def _quota_ownership_distribution(data: dict) -> dict:
    regimes = data["regimes"]
    agents = list(regimes["global_quota"]["individual"])
    x = np.arange(len(agents))
    width = 0.34
    figure, (left, right) = plt.subplots(1, 2, figsize=(9.4, 4.3))
    for offset, (key, label, color) in zip(
        (-width / 2, width / 2),
        (
            ("global_quota", "Global quota", COLORS[0]),
            ("cap_and_trade", "Cap and trade", COLORS[1]),
        ),
    ):
        individual = regimes[key]["individual"]
        electricity = [
            individual[agent]["own_electricity_component_not_paper_cardinal_utility"]
            for agent in agents
        ]
        policy_income = [
            individual[agent]["income_decomposition"]["policy_income"]
            for agent in agents
        ]
        left.bar(x + offset, electricity, width, label=label, color=color)
        right.bar(x + offset, policy_income, width, label=label, color=color)
    for axis in (left, right):
        axis.set_xticks(x, agents)
        axis.grid(axis="y", alpha=0.25)
        axis.legend(frameon=False)
    left.set_ylabel("Individual electricity consumption")
    left.set_title("Allocation")
    right.set_ylabel("Policy income")
    right.set_title("Quota-right income")
    figure.suptitle("Distributional Effect of Quota Property Rights at Fixed Emissions")
    caption = (
        "Total emissions remain fixed at 3. The panels report individual electricity "
        "consumption and policy income, not a cardinal social-welfare aggregate."
    )
    _finish(
        figure,
        "quota_ownership_welfare.png",
        caption,
        "results/milestone10_welfare_distribution.json",
    )
    return {
        "caption": caption,
        "source": "results/milestone10_welfare_distribution.json",
    }


def _finite_approximation(data: dict) -> dict[str, dict]:
    rows = data["finite_results"]
    sizes = [row["N"] for row in rows]
    prices = np.asarray([row["prices"] for row in rows])
    emissions = [row["emissions_unabsorbed_bad"] for row in rows]

    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    axis.plot(sizes, prices[:, 0], marker="o", color=COLORS[1], label="Bad price")
    axis.plot(sizes, prices[:, 1], marker="s", color=COLORS[0], label="Good price")
    axis.set_xlabel("Finite population size N")
    axis.set_ylabel("Signed price")
    axis.set_title("Finite Weighted Approximation Prices")
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    price_caption = (
        "Signed prices for midpoint finite approximations of the explicit continuum-type "
        "target; this stability is construction-specific, not a general convergence proof."
    )
    _finish(
        figure,
        "finite_approximation_prices.png",
        price_caption,
        "results/milestone11_finite_weighted_lab.json",
    )

    figure, axis = plt.subplots(figsize=(7.2, 4.2))
    axis.plot(sizes, emissions, marker="o", color=COLORS[2], label="Unabsorbed bad")
    axis.axhline(0.0, color="#333333", linewidth=1.0, label="Continuum target")
    axis.set_xlabel("Finite population size N")
    axis.set_ylabel("Aggregate unabsorbed bad")
    axis.set_title("Finite Weighted Approximation Emissions")
    axis.set_ylim(-0.02, 0.02)
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    emission_caption = (
        "All midpoint economies exactly match the zero-unabsorbed-bad target up to floating-"
        "point error; the experiment is paper-inspired and finite-dimensional."
    )
    _finish(
        figure,
        "finite_approximation_emissions.png",
        emission_caption,
        "results/milestone11_finite_weighted_lab.json",
    )
    return {
        "finite_approximation_prices.png": {
            "caption": price_caption,
            "source": "results/milestone11_finite_weighted_lab.json",
        },
        "finite_approximation_emissions.png": {
            "caption": emission_caption,
            "source": "results/milestone11_finite_weighted_lab.json",
        },
    }


def _branch_diagram(data: dict) -> dict:
    figure, axis = plt.subplots(figsize=(7.2, 4.4))
    rows = data["tax_emissions_correspondence"]
    branch_ids = sorted(
        {item["equilibrium_id"] for row in rows for item in row["equilibria"]}
    )
    for branch_id in branch_ids:
        points = [
            (row["table_goods_sum_tax_rate"], item["eta_p1_over_p2"])
            for row in rows
            for item in row["equilibria"]
            if item["equilibrium_id"] == branch_id
        ]
        if points:
            axis.plot(
                *zip(*points),
                marker="o",
                color=COLORS[branch_id % len(COLORS)],
                label=f"Discovered branch {branch_id + 1}",
            )
    axis.set_xlabel("Emission tax rate (paper goods-sum convention)")
    axis.set_ylabel("Equilibrium price ratio eta = p1/p2")
    axis.set_title("Verified Candidate Branch Diagram")
    axis.grid(alpha=0.25)
    axis.legend(frameon=False)
    caption = (
        "Continuation and fresh multistart reveal three candidate branches at low tax rates "
        "and one at intermediate rates; missing candidates are not a proof of nonexistence."
    )
    _finish(
        figure,
        "equilibrium_branch_diagram.png",
        caption,
        "results/milestone9_tax_quota_sweeps.json",
    )
    return {"caption": caption, "source": "results/milestone9_tax_quota_sweeps.json"}


def run() -> dict:
    FIGURES.mkdir(parents=True, exist_ok=True)
    milestone9 = _load("milestone9_tax_quota_sweeps.json")
    milestone10 = _load("milestone10_welfare_distribution.json")
    milestone11 = _load("milestone11_finite_weighted_lab.json")
    required_statuses = {
        "milestone9_tax_quota_sweeps.json": "SWEEP_SUCCESS",
        "milestone10_welfare_distribution.json": "WELFARE_DISTRIBUTION_SUCCESS",
        "milestone11_finite_weighted_lab.json": "FINITE_WEIGHTED_EXPERIMENT_SUCCESS",
    }
    source_data = {
        "milestone9_tax_quota_sweeps.json": milestone9,
        "milestone10_welfare_distribution.json": milestone10,
        "milestone11_finite_weighted_lab.json": milestone11,
    }
    mismatches = {
        filename: {
            "expected": expected,
            "actual": source_data[filename].get("status"),
        }
        for filename, expected in required_statuses.items()
        if source_data[filename].get("status") != expected
    }
    if mismatches:
        raise ValueError(f"Refusing to generate figures from failed sources: {mismatches}")
    figures = {
        "tax_emission_correspondence.png": _tax_emission_correspondence(milestone9),
        "quota_price_correspondence.png": _quota_price_correspondence(milestone9),
        "quota_ownership_welfare.png": _quota_ownership_distribution(milestone10),
        **_finite_approximation(milestone11),
        "equilibrium_branch_diagram.png": _branch_diagram(milestone9),
    }
    source_files = sorted({entry["source"] for entry in figures.values()})
    manifest = {
        "status": "FIGURE_GENERATION_SUCCESS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "figures": figures,
        "source_sha256": {
            source: _sha256(ROOT / source) for source in source_files
        },
    }
    write_json(FIGURES / "figure_manifest.json", manifest)
    readme_lines = [
        "# Figures",
        "",
        "All figures are generated from persisted experiment JSON. Captions preserve the scope of the numerical claims.",
        "",
    ]
    for filename, entry in figures.items():
        readme_lines.extend(
            [
                f"## {filename}",
                "",
                entry["caption"],
                "",
                f"Source: `{entry['source']}`.",
                "",
            ]
        )
    (FIGURES / "README.md").write_text("\n".join(readme_lines), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    print(run()["status"])
