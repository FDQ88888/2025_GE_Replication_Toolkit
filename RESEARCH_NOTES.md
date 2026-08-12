# Duanmu GE Lab - Research Notes

> Status: Continuously maintained research-design document. Initial version: 2026-08-09; official Supplement source audit added 2026-08-10. See the individual milestone reports for implementation status.

## 0. Research Discipline and Evidence Labels

This project follows `MATHEMATICAL MODEL FIRST. CODE SECOND.` Every mathematical object entering the code must cite its source and distinguish among:

- **PAPER DEFINITION**: a definition, assumption, theorem, or example from the original article or Supplement.
- **OUR COMPUTATIONAL CHOICE**: an additional utility function, technology-set parameterization, normalization coordinates, solver, or tolerance selected for finite-dimensional computation.
- **NUMERICAL APPROXIMATION**: an approximation using finite grids, multistart search, discrete populations, or residual criteria; it must not be presented as an existence proof.

Any formula not yet checked against a primary source must be labeled `NOT VERIFIED FROM PRIMARY SOURCE` and must not be the default in paper-replication mode.

## 1. Materials Reviewed and Source Status

### 1.1 User-Provided Materials

- `Three proofs.pdf`: 11 pages of handwritten proofs covering the Slutsky matrix, Kakutani-Nash existence, and the Second Welfare Theorem.
- `Proof of Microeconomics.pdf`: 14 pages of handwritten proofs covering separation/supporting hyperplanes, Slutsky, vNM expected utility, Debreu representation, Berge's Maximum Theorem, Kakutani, Walrasian-equilibrium existence, and the First and Second Welfare Theorems.
- `Haosui_Duanmu_CV.pdf`: local CV dated January 2025.
- `pasted-text.txt`: project brief requiring a research-grade, definition-driven finite weighted GE project with bads, production, externalities, quotas, emission taxes, and independent diagnostics.

### 1.2 Primary Research Literature

1. Robert M. Anderson and Haosui Duanmu, "Cap-and-Trade and Carbon Tax Meet Arrow-Debreu," *Econometrica* 93(2), 2025, pp. 357-393. The official full text was obtained and verified: [Econometric Society PDF](https://www.econometricsociety.org/publications/econometrica/2025/03/01/Cap-and-Trade-and-Carbon-Tax-Meet-ArrowDebreu/file/ecta200778.pdf).
2. Robert M. Anderson, Haosui Duanmu, M. Ali Khan, and Metin Uyanik, "Existence of Equilibria in Large Competitive Markets with Bads, Production and Comprehensive Externalities," arXiv:2511.00478v2, revised 2026-05-31. The [full arXiv HTML](https://arxiv.org/html/2511.00478v2) and PDF were verified.
3. Haosui Duanmu's local CV and personal research page. His earlier page emphasizes mathematical logic, nonstandard analysis, statistics, and probability; the CV shows that his recent research has expanded into mathematical economics, general equilibrium, climate policy, bads, and externalities. [Personal website](https://hyperfinite.net/)

### 1.3 Supplement Source Audit, 2026-08-10

The Supplementary Material for the 2025 *Econometrica* article was obtained from the official Econometric Society location and stored as:

```text
sources/Anderson_Duanmu_2025_Supplement.pdf
```

File verification: 17 pages, 423,234 bytes, PDF 1.5, SHA-256 `A5013517781FCD37BF38446975DA2F91C033FDEC6709AFF90F702C1652C8524A`. Wiley lists the same attachment as `ecta200778-sup-0001-onlineappendix.pdf` (Online Appendix, 413.3 KB). The official article was also archived as `sources/Anderson_Duanmu_2025_Econometrica.pdf`.

Section 3 of the Supplement provides detailed analyses of Examples 1-4: Example 1 on pp. 11-12, Example 2 on pp. 12-13, Example 3 on pp. 13-15, and Example 4 on pp. 15-16. Examples 5-6 are not separate sections there, but Examples 5-6 in the article (journal pp. 382-384) are built entirely on the economies and equilibrium branches of Examples 3-4. The article and Supplement together therefore clear the primary-source gate for Examples 3-6. A parameter-by-parameter and formula-by-formula ledger is still required before coding each example; chart values alone are insufficient.

"The Second Welfare Theorem for Quota Equilibrium" and other works in progress listed in the CV remain available only as bibliographic records or separate working-paper references. Their definitions must not enter the core implementation before the full manuscripts are verified.

## 2. Professor Haosui Duanmu's Research and This Project's Position

The research strands most relevant to this project, based on the CV and published papers, are:

- mathematical economics and general-equilibrium existence;
- production economies, bads, non-free-disposal, and potentially negative prices;
- comprehensive externalities caused by consumption and production;
- cap-and-trade, quota equilibrium, and carbon/emission-tax equilibrium;
- quota-right allocation, tax rebates, and welfare distribution;
- extensions from finite weighted economies to measure economies;
- nonstandard analysis, hyperfinite economies, and Loeb-measure methods.

Directly relevant published work in the CV includes:

- Anderson and Duanmu (2025), *Econometrica*: quotas and emission taxes in an Arrow-Debreu production economy.
- Anderson, Duanmu, Khan, and Uyanik (2022), *Economic Theory*: Walrasian equilibrium with infinitely many agents, with and without free disposal.
- Anderson and Duanmu (2025), *Games and Economic Behavior*: equilibrium and social norms.
- Anderson, Duanmu, Khan, and Uyanik (2022), *Journal of Mathematical Economics*: abstract economies in locally convex topological vector spaces.

The appropriate scholarly position of `Duanmu GE Lab` is therefore: **auditable finite-dimensional computational research on general-equilibrium models related to Professor Duanmu's work, providing tools for future study of bads, externalities, policy, and large-economy approximation**. It is neither a SAM/GTAP-based calibrated macro CGE nor a routine representative-household Cobb-Douglas demonstration of a "carbon-tax effect."

## 3. The Finite Quota Economy in Anderson-Duanmu (2025)

Everything below is a **PAPER DEFINITION**, primarily from Definitions 3.1-3.5, pp. 363-366.

### 3.1 Basic Objects

- A finite set of agents: `Omega`.
- A finite set of producers: `J`. A quota economy includes government firm `j=0`, with `Y_0={0}`.
- `l` commodities; the first `k` are government-regulated.
- Each consumption set `X_omega subset R_+^l` is nonempty, closed, and convex.
- Each production set `Y_j subset R^l` is nonempty; production vectors use net-output notation.
- Allocation space `A = product_omega X_omega`.
- Global preferences may depend on other agents' consumption, every firm's production, and prices; given these external states, an agent chooses only its own consumption.
- `theta_omega_j >= 0` is the agent's ownership share in firm `j`, with `sum_omega theta_omega_j = 1` for each firm.
- `e_omega in R_+^l` is the initial endowment.

### 3.2 Signed Prices and Normalization

The paper's price set is

```text
Delta = {p in R^l : ||p||_1 = sum_n |p_n| = 1}.
```

Negative prices are explicitly permitted and may represent the prices of bads or emissions. The quota price is the negative of regulated commodity prices: `q = -proj_k(p)`.

This produces two concepts that must not be confounded:

- **Price normalization**: remove homogeneity, for example with `||p||_1=1` or a numeraire.
- **Price-sign restrictions**: determine whether particular coordinates may be negative, zero, or positive.

The code must not use softmax to force every price to be positive.

### 3.3 Quota Rights and the Compliance Region

The government allocates quotas for regulated commodities to firm `j`. The paper writes

```text
m^(j) in R_<=0^k
```

for the negative of the firm's quota and defines `m = sum_j m^(j)`. Thus `-m^(j)` is firm `j`'s emission right and `-m` is the aggregate quota.

The quota-compliance region is

```text
Z(m) = {m} x product_{k<n<=l} Z(m)_n,
```

where each unregulated coordinate `Z(m)_n` may be `{0}` (exact market clearing) or `R_<=0` (free disposal). Disposal must therefore be configured commodity by commodity rather than hidden in a global default.

Two polar regimes are:

- **cap-and-trade**: all quota rights belong to private firms;
- **global quota equilibrium**: all quota rights belong to the government firm, with its ownership shares determining the income rebate.

### 3.4 Budgets, Profits, and Demand

An agent's quota budget set is

```text
B^m_omega(y,p) = {
  z in X_omega :
  p*z <= p*e_omega
         + sum_j theta_omega_j [p*y_j + proj_k(p)*m^(j)]
}.
```

Firm `j`'s profit is

```text
pi_j^m(p,y_j) = p*y_j + proj_k(p)*m^(j).
```

The quota-right term is constant in `y_j`, so firm supply still satisfies

```text
S_j^m(p) = argmax_{z in Y_j} p*z.
```

Aggregate quotas and their ownership distribution nevertheless affect production, consumption, and welfare indirectly through equilibrium prices, firm profits, and household incomes. The government firm's profit comes entirely from selling its quota and is returned to agents according to government-firm ownership shares set by the government.

### 3.5 Quota Equilibrium

`(x_bar, y_bar, p_bar)` is a `Z(m)`-compliant quota equilibrium if and only if:

1. every agent's `x_bar_omega` belongs to its demand set at the given external state and prices;
2. every firm plan `y_bar_j` maximizes profit at `p_bar`;
3. the aggregate resource residual satisfies

```text
sum_omega x_bar_omega
- sum_omega e_omega
- sum_j y_bar_j in Z(m).
```

For regulated coordinates, aggregate net emissions therefore equal the preset aggregate quota exactly. For unregulated coordinates, `Z(m)_n` determines whether exact clearing or surplus is permitted.

### 3.6 Verified Theorems and Examples

| Conclusion | Logical status in the paper | Implementation implication |
|---|---|---|
| A quota equilibrium exists for every feasible quota satisfying the assumptions | **Theorem 1**, pp. 370-371 | Numerical failure is not nonexistence; first inspect assumptions, parameterization, and the solver |
| With externalities generated only by aggregate net emissions and no free disposal of unregulated goods, quota equilibrium is constrained weakly Pareto optimal among allocations with the same emissions | **Theorem 2**, pp. 373-374 | Welfare diagnostics must compare at fixed aggregate emissions and cannot claim unconstrained global Pareto optimality |
| Quota-right allocations affect consumption and individual welfare | **Example 2** | Quota rights, firm ownership, and rebate rules must be first-class data |
| Every quota equilibrium can be implemented as an emission-tax equilibrium with the corresponding tax rate and rebate rule | **Theorem 3**, p. 376 | The mapping depends on prices and rebates; the two policy objects are not automatically equivalent |
| Every emission-tax equilibrium can be implemented as a global quota equilibrium | **Theorem 4**, p. 377 | The corresponding aggregate quota is determined by endogenous emissions in that tax equilibrium |
| Certain tax rates have no emission-tax equilibrium | **Examples 3-4**, not a general nonexistence theorem | Tax sweeps must record regions with no candidate, but solver failure cannot be labeled nonexistence |
| One tax rate can correspond to different emission levels | Multiple-equilibrium phenomenon in **Examples 3-4** | Multistart and branch tracking are required; retaining one root is insufficient |
| One quota can correspond to different quota prices | Multiple-equilibrium phenomenon in **Examples 3-6** | A quota implements a target quantity, but its price need not be unique |

Replication status after obtaining the Supplement:

| Example | Primary-source status | Dependency |
|---|---|---|
| Example 1 | `SOURCE_READY` | Complete production and quota accounting first |
| Example 2 | `SOURCE_READY` | Example 1 architecture, second firm, and property-right allocation |
| Example 3 | `SOURCE_READY` | Emission-tax accounting, nonlinear demand, and multiple-root search |
| Example 4 | `SOURCE_READY` | Linear technology, boundary supply correspondence, and continuum of equilibria |
| Example 5 | `SOURCE_READY` | Every branch of Example 3 and quota/tax mappings |
| Example 6 | `SOURCE_READY` | Every branch of Example 4 and quota/tax mappings |

## 4. The Emission-Tax Economy in Anderson-Duanmu (2025)

The following is a **PAPER DEFINITION** from Definition 4.1, Remark 4.2, and Definition 4.3, pp. 375-376.

### 4.1 Policy Objects

- Every firm is private; the tax model has no government firm from the quota model.
- `lambda_omega >= 0` is the government's rebate share, with `sum_omega lambda_omega = 1`.
- Compliance-region coordinates for the first `k` regulated commodities are `R_<=0`, permitting arbitrary net emissions subject to an emission tax.
- `t` is the vector of emission-tax rates on the first `k` commodities.

Aggregate net emissions are

```text
C(x,y) = proj_k(
  sum_omega e_omega + sum_j y_j - sum_omega x_omega
).
```

Government tax revenue is `t*C(x,y)` and is returned according to `lambda`.

### 4.2 Tax Budgets and Equilibrium

An agent's budget set is

```text
B^t_omega(x,y,p) = {
  z in X_omega :
  p*z <= p*e_omega
         + sum_j theta_omega_j p*y_j
         + lambda_omega t*C(x,y)
}.
```

`(x_bar,y_bar,p_bar)` is an emission-tax equilibrium if and only if:

1. `proj_k(p_bar) = -t`, so the tax rate fixes the negative price of regulated commodities;
2. every consumer is optimal in a budget set including rebate income;
3. every firm maximizes `p_bar*y_j`;
4. the aggregate resource residual belongs to the tax model's compliance region `V`.

The government specifies tax rates and rebates in advance; aggregate net emissions are endogenous to equilibrium. This creates an important numerical-scale issue: the paper imposes both `||p||_1=1` and `proj_k(p)=-t`. The tax rate is therefore a relative price in the normalized price system, and code-level tax sweeps must be interpreted jointly with the normalization convention.

## 5. Large Economies, Bads, and Comprehensive Externalities

This section follows the **PAPER DEFINITION** in arXiv:2511.00478v2.

### 5.1 Measure Production Economy

Definition 4.2 represents consumers by a probability space `(Omega,B,mu)`, while retaining a finite set of firms. Key objects include:

- an integrable allocation `x in L1(Omega,R_+^l)`;
- production vector `y in product_j Y_j`;
- signed normalized price `p in Delta`, where `||p||_1=1`;
- global preferences that may depend on the full consumption allocation, all firms' production, prices, and own consumption;
- ownership densities `theta_omega_j` satisfying `integral theta_omega_j dmu = 1`;
- endowment density `e in L1`.

Budgets and firm profit maximization retain the Arrow-Debreu structure of the finite economy. Equilibrium without free disposal requires exact market clearing:

```text
integral x dmu - integral e dmu - sum_j y_j = 0.
```

### 5.2 A Bad Is Not Merely an Enumeration Label

For technical assumptions, the paper treats the first `k` commodities as a "class of bads," with integrably bounded projections of consumption sets; the remaining commodities permit unbounded consumption. It explicitly notes, however, that agents need not agree that an object is a bad and that the same object may be mixed manna.

Consequently, `CommodityKind.GOOD/BAD` in the code is used only for semantics, configuration validation, and default diagnostics. It must not automatically imply:

- that every agent is monotonically increasing or decreasing in it;
- that its price is necessarily positive or negative;
- that it can be freely disposed of;
- that it is necessarily regulated.

### 5.3 Non-Free-Disposal and Negative Prices

The paper's economic logic is that production byproducts cannot disappear from accounting. If disposal of a bad creates externalities, negative prices must be allowed to incentivize absorption, elimination, or sequestration. Strong monotonicity and free disposal in production would exclude the necessary negative prices and therefore cannot be default assumptions.

Consumers' capacity to absorb bads requires an integrable bound. This assumption avoids the phenomenon in Hara (2005), where equilibrium allocations in finite economies lack uniform integrability and a vanishingly small population absorbs nearly all bads.

### 5.4 Finite Weighted and Measure-Economy Theorems

- **Theorem 1**: equilibrium exists in a finite weighted production economy under convex preferences, feasibility/survival, and production-set conditions.
- **Theorem 2**: equilibrium exists in a measure production economy under conditions including a Polish consumer space, integrably bounded consumption of bads, and weak-topology continuity of preferences.
- **Supplementary Theorem 3**: adds a positive emission bound to a measure quota economy and establishes quota-equilibrium existence.

The proof route is: finite weighted theorem -> hyperfinite lifting -> transfer principle -> equilibrium in the Loeb economy -> projection back to the original measure economy under stronger continuity.

### 5.5 What This Project Can Do and Claim

Python can implement a finite weighted economy and interpret weights `lambda_i` as atomic probability masses. Increasing the finite number of agents can be used to study numerical stability, empirical distributions, and approximation behavior.

However:

- finite discretization is not a Loeb-measure construction;
- stability across several finite samples is not an existence proof for a measure economy;
- numerical convergence plots do not prove uniform integrability, weak compactness, or measurable selection;
- the first stage of this project does not implement hyperreal numbers, hyperfinite objects, or the transfer principle.

## 6. Connection Between the User's Proof Background and the Project

### 6.1 `Three proofs.pdf`

- **Slutsky matrix**: the notes form a chain from the expenditure function and Shephard's lemma to symmetry and negative semidefiniteness. This can support analytical benchmarks, comparative statics, and derivative checks in the individual-demand module. Before entering formal theoretical documentation, differentiability, interiority, uniqueness, and local/global optimality conditions must be made explicit.
- **Kakutani-Nash**: nonempty and convex-valued best-response correspondences, closed graph/upper hemicontinuity, and a compact convex domain form the correct skeleton. This directly relates to correspondence-based existence arguments in general equilibrium, but code can only validate residuals in a finite instance; it cannot "compute Kakutani's theorem."
- **Second Welfare Theorem**: the central line through convex separation, supporting prices, and wealth transfers is correct and is the best entry point for understanding quota ownership, government rebates, and supporting prices. Local nonsatiation, convexity, feasible-set geometry, nonzero prices, and conditions that strengthen quasi-equilibrium to equilibrium must remain explicit.

### 6.2 `Proof of Microeconomics.pdf`

These notes already cover the theoretical toolkit required by the project: support/separation, maximum theorems, fixed points, Walrasian-equilibrium existence, and welfare theorems. The main issue is not too few proofs, but that some proofs compress theorem assumptions, continuity notions for correspondences, and boundary cases too aggressively.

Future versions should rewrite each proof as a five-part research note:

1. precise theorem statement;
2. assumption inventory and where each assumption is used;
3. principal lemmas in the proof;
4. vulnerable boundaries or counterexamples;
5. implications for the computational model.

## 7. Mathematical Object -> Code Object Map

| Mathematical object | Planned code object | First-round semantic constraint |
|---|---|---|
| Consumer/agent | `Consumer` | ID, population weight, endowment, ownership, quota rights/government rebates, preferences, and externality exposure |
| Firm | `Firm` | Technology, ownership, inputs/outputs, bad byproducts, and policy accounting |
| Commodity | `Commodity` | Name, index, semantic kind, regulation status, and clearing regime; kind does not determine signs or disposal |
| Endowment vector | `EndowmentVector` or array field | Strict validation of dimension and commodity order |
| Preferences | `PreferenceModel` / `UtilityModel` | The paper permits incomplete preferences; a computational MVP must explicitly choose a numerically optimizable representation |
| Production set | `ProductionTechnology` | Represented by constraints/feasible sets, without deleting emission byproducts from accounting |
| Externality | `ExternalityModel` | Independent of utility form; computes a state or preference parameter from `(x,y,p)` |
| Economy | `Economy` | Aggregates consumers, firms, commodities, weights, property rights, and clearing rules |
| Policy | `PolicyBase` | Generates budget adjustments, firm income, policy constraints, and accounting diagnostics in one place |
| No regulation | `NoRegulation` | Does not imply free disposal for every commodity |
| Quota | `QuotaPolicy` | Aggregate quota, firm quotas, government quota, compliance region, and quota price |
| Emission tax | `EmissionTaxPolicy` | Tax-rate vector, rebate vector, tax revenue, and regulated-price restrictions |
| Equilibrium equations | `EquilibriumSystem` | Variable encoding, constraints, and residuals, decoupled from the solver |
| Candidate solution | `EquilibriumCandidate` | Raw variables, state, originating start, solver status, and residuals |
| Validator | `EquilibriumDiagnostics` | Independently recomputes optimality, clearing, budgets, policy accounting, normalization, and complementarity conditions |

## 8. Design Invariants That Must Be Frozen

1. Paper definitions, computational choices, and numerical approximations must be labeled separately in documentation, configuration, and output.
2. Price normalization and price-sign restrictions are separate modules.
3. Free disposal is not the default; each commodity's clearing condition is configured explicitly.
4. Policy income is computed in one policy-accounting layer, which serves as the common mathematical source for consumer budgets and diagnostics.
5. A solver's success return is not an equilibrium; every equilibrium candidate must pass independent diagnostics.
6. Solver failure is not a nonexistence proof. "No equilibrium" may cite only a paper theorem/example; otherwise report "no candidate discovered under the specified search protocol."
7. Multiple-equilibrium research retains all candidates after clustering/deduplication, failed starting points, and branch information.
8. Finite-population experiments are described only as finite weighted computations or finite approximations, without claims to implement measure-economy or nonstandard-analysis proofs.

## 9. First-Round Conclusion

The most reliable direction was to build a finite GE core supporting signed prices, production, externalities, and commodity-level clearing rules before attempting a comprehensive carbon-tax simulator. The paper's `QuotaPolicy` and `EmissionTaxPolicy` would then be implemented separately, targeting the analytical results of Examples 1-2 and the multiple-equilibrium phenomena of Examples 3-6.

Subsequent core code had to continue respecting the module-level `BLOCKING` gates in `OPEN_QUESTIONS.md`. The missing-Supplement issue was resolved; attention shifted to production accounting, example-specific parameter ledgers, quota/tax-rate normalization, and independent optimality diagnostics.

## 10. Milestone 5 Quota-Replication Conclusions

The finite quota accounting in Definitions 3.2-3.5 has been implemented and validated against Examples 1-2:

- emissions remain coordinates of the original commodity space; no permit commodity is added;
- `m^(j)<=0` is the signed representation of firm emission rights, with `m=sum_j m^(j)`;
- firm total profit is `p dot y_j + proj_k(p) dot m^(j)`;
- the government firm has `Y_0={0}`, and its income is distributed through government-firm ownership;
- consumer budgets and diagnostics share `QuotaEconomy.income_breakdowns`;
- the formal policy Walras check is `p dot r - proj_k(p) dot m=0`;
- in Example 2, changing only property rights changes individual incomes and consumption distributions while aggregate quota, prices, technology, and aggregate consumption remain fixed.

The original text of Example 2 provides no cardinal utility functions. The project therefore reproduces agent-level electricity consumption and welfare ordering at the same emission level without fabricating "paper utility values." See `MILESTONE_5_QUOTA_REPORT.md` for complete evidence.

## 11. Milestone 6 Tax Accounting and Mapping Conclusions

The emission tax `t` shares a scale with signed-L1 prices and must satisfy `proj_k(p)=-t`. A numeraire conversion must therefore rescale `p` and `t` together; converting only one changes the economic problem.

Tax budgets use `C(x,y)` and `t dot C(x,y)` generated by the candidate allocation. The global-quota candidate in Example 1 is mapped to a tax candidate using the Theorem 3 formula and then mapped back to a global-quota candidate under Theorem 4. Both endpoints pass independent diagnostics. This is a numerical check of the theoretical mappings and does not replace the paper's proofs.

## 12. Multiple-Equilibrium Evidence from Examples 3-6

Example 3 shows that one tax rate can correspond to several price ratios and emission levels. Example 5 further shows that when a tax rate is chosen to deliver 30% abatement on one branch, the other two branches still produce different abatement levels. The linear technology in Examples 4/6 produces a continuum of emissions at `t=1/4`. By contrast, a quota fixes the regulated resource difference directly at `m`, while Example 5 gives three different quota prices for the same quota.

These results support representing a correspondence, rather than a single-valued function, in figures and data structures. Numerical programs retain every verified branch, neither averaging branches nor keeping only the first root.
