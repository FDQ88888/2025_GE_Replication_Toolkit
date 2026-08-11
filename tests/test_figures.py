from pathlib import Path

import pytest

import scripts.generate_figures as generate_figures
from scripts.generate_figures import ROOT, run


def test_research_figures_have_captions_and_sources() -> None:
    manifest = run()

    assert manifest["status"] == "FIGURE_GENERATION_SUCCESS"
    assert len(manifest["figures"]) == 6
    for filename, metadata in manifest["figures"].items():
        path = ROOT / "figures" / filename
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
        assert path.stat().st_size > 10_000
        assert metadata["caption"]
        assert Path(metadata["source"]).suffix == ".json"


def test_figure_generation_rejects_failed_source(monkeypatch: pytest.MonkeyPatch) -> None:
    original_load = generate_figures._load

    def failed_load(filename: str) -> dict:
        result = original_load(filename)
        if filename == "milestone9_tax_quota_sweeps.json":
            result["status"] = "SWEEP_FAILURE"
        return result

    monkeypatch.setattr(generate_figures, "_load", failed_load)
    with pytest.raises(ValueError, match="Refusing to generate figures"):
        generate_figures.run()
