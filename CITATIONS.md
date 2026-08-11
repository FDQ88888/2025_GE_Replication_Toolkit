# Citations

## Research Context

Anderson, Robert M., and Haosui Duanmu. 2025. “Cap-and-Trade and Carbon Tax Meet Arrow-Debreu.” *Econometrica* 93(2): 357-393. DOI: [10.3982/ECTA22923](https://doi.org/10.3982/ECTA22923). [Econometric Society official PDF](https://www.econometricsociety.org/publications/econometrica/2025/03/01/Cap-and-Trade-and-Carbon-Tax-Meet-ArrowDebreu/file/ecta200778.pdf).

Anderson, Robert M., and Haosui Duanmu. 2025. “Supplement to ‘Cap-and-Trade and Carbon Tax Meet Arrow-Debreu.’” *Econometrica Supplemental Material* 93. [Econometric Society official Supplement PDF](https://www.econometricsociety.org/publications/econometrica/2025/03/01/Cap-and-Trade-and-Carbon-Tax-Meet-ArrowDebreu/supp/22923SUPP.pdf). Wiley lists the same file as `ecta200778-sup-0001-onlineappendix.pdf` (Online Appendix, 413.3 KB).

Anderson, Robert M., Haosui Duanmu, M. Ali Khan, and Metin Uyanik. 2026. “Existence of Equilibria in Large Competitive Markets with Bads, Production and Comprehensive Externalities.” arXiv:2511.00478v2. [arXiv HTML](https://arxiv.org/html/2511.00478v2).

Mas-Colell, Andreu, Michael D. Whinston, and Jerry R. Green. 1995. *Microeconomic Theory*. Oxford University Press.

## Primary-Source Verification During Development

The official PDFs were consulted and archived locally during development for source verification. Copyrighted paper PDFs and local extraction files are **not redistributed in the clean source package**. Official retrieval links, bibliographic details, source locations, and the available verification hash are recorded here so a collaborator can retrieve the authoritative files independently.

- `sources/Anderson_Duanmu_2025_Econometrica.pdf`: 37 PDF pages; official journal pp. 357-393.
- `sources/Anderson_Duanmu_2025_Supplement.pdf`: 17 pages, 423,234 bytes, SHA-256 `A5013517781FCD37BF38446975DA2F91C033FDEC6709AFF90F702C1652C8524A`.
- Corresponding `.txt` extraction aids were used locally; the official PDFs remain authoritative and neither file type is part of the clean delivery archive.

Supplement section map used by the replication plan:

| Material | PDF pages | Replication use |
|---|---:|---|
| Rebate Walras Law | 3-6 | Policy-accounting identity and diagnostics |
| Detailed Analysis of Example 1 | 11-12 | Quota benchmark and unique closed-form equilibrium |
| Detailed Analysis of Example 2 | 12-13 | Ownership/quota-allocation welfare comparison |
| Computation of Demands in Example 3 | 13-15 | Nonlinear demand branches and numerical root variable |
| Detailed Analysis of Example 4 | 15-16 | Tax existence boundary and continuum of emissions equilibria |
| Main-paper Examples 5-6 | journal pp. 382-384 | Quota/tax inequivalence built from Examples 3-4 |

## Milestone 1 Scope

The 2-consumer x 2-good Cobb-Douglas economy in this milestone is a software-validation benchmark specified in the project brief. It is not a replication of Anderson and Duanmu (2025).

The closed-form Marshallian demand used here is

```text
x_l(p,w) = alpha_l w / p_l,
```

under strictly positive prices, positive Cobb-Douglas shares, and shares summing to one. The benchmark's full derivation is recorded in [docs/analytical_benchmark.md](docs/analytical_benchmark.md).

## Software

- NumPy documentation: <https://numpy.org/doc/stable/>
- SciPy `root_scalar`: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root_scalar.html>
- pytest documentation: <https://docs.pytest.org/>
