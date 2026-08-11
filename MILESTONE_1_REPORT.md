# Duanmu GE Lab - Milestone 1 Report

> **历史报告说明（2026-08-09）**：本文件记录最初的 Milestone 1 交付。后续审计发现其中把候选资源残差与重新优化需求残差混写的问题；当前实现和最终验证语义以 `MILESTONE_1_1_AUDIT_REPORT.md` 为准。本文件不再作为当前 diagnostics 的规范说明。

> 完成日期：2026-08-09  
> 范围：Minimal General Equilibrium Engine  
> 状态：完成并停止；未进入 Production、Quota、Emission Tax、Bads、Externalities 或 Finite Approximation。

## 1. What Was Implemented

本轮建立了一个可安装、可测试、可在 Windows + VS Code + Python 3.11+ 运行的有限交换经济核心。已经完成的计算链为：

```text
economic parameters
-> Consumer
-> closed-form individual demand
-> ExchangeEconomy
-> aggregate excess demand
-> FixedNumeraire
-> scalar equilibrium solver
-> EquilibriumCandidate
-> independent EquilibriumDiagnostics
-> VERIFIED_CANDIDATE
```

实现对象包括：

- `Commodity`、`CommodityKind`、`ClearingRule`；
- 抽象 `PreferenceModel` 与 `CobbDouglasUtility`；
- `Consumer` 与禀赋财富、需求、效用、预算 residual；
- `ExchangeEconomy` 与聚合禀赋、需求、超额需求、逐市场 residual、Walras residual；
- 抽象 `PriceNormalization`、`FixedNumeraire` 和 signed L1 报告归一化；
- 2-good、1-independent-price 的 `ExchangeEquilibriumSolver`；
- 不带验证结论的 `EquilibriumCandidate`；
- `NumericalTolerances`、四级 candidate classification 和独立 diagnostics；
- 解析 benchmark、命令行脚本、JSON 结果和 26 个自动测试。

## 2. Mathematical Benchmark

当前 benchmark 是 `SOFTWARE VALIDATION BENCHMARK`，不是 Anderson-Duanmu paper replication。

消费者 1：

```text
omega_1 = (1,0)
u_1(x_11,x_12) = x_11^(1/2) x_12^(1/2)
```

消费者 2：

```text
omega_2 = (0,1)
u_2(x_21,x_22) = x_21^(1/2) x_22^(1/2)
```

第二种商品是 numeraire：`p_2=1`。超额需求在全项目中固定定义为：

```text
z(p) = aggregate demand - aggregate endowment.
```

## 3. Analytical Equilibrium

Cobb-Douglas Marshallian demand 为：

```text
x_l = alpha_l w / p_l.
```

在 `alpha_1=alpha_2=1/2` 下：

```text
w_1 = p_1
w_2 = 1

z_1(p_1,1) = -1/2 + 1/(2p_1)
z_2(p_1,1) = (p_1-1)/2
```

求解 `z_1=0` 得：

```text
p* = (1,1)
x_1* = (1/2,1/2)
x_2* = (1/2,1/2)
```

完整手工推导见 `docs/analytical_benchmark.md`。

## 4. Numerical Method

- 价格坐标：`FixedNumeraire(index=1, value=1.0)`；
- 独立未知量：`p_1`；
- 只求解：`z_1(p_1,1)=0`；
- 未用于求根的市场：商品 2，由 diagnostics 检查；
- 方法：SciPy `root_scalar(..., method="brentq")`；
- bracket：`[0.05,20.0]`；
- `xtol=1e-13`，`rtol=1e-13`，`maxiter=100`。

求解器没有同时向一个未知量强加两个市场方程，也没有用 Walras law 修改或替代 residual。

## 5. Solver Result

实际运行结果：

```text
solver method      = brentq
solver success     = true
iterations         = 13
function calls     = 14
numerical prices   = [1.0, 1.0]
allocations        = [[0.5,0.5], [0.5,0.5]]
price L2 distance  = 0.0
allocation distance= 0.0
```

signed L1 报告价格为 `[0.5,0.5]`。这一步只用于报告，没有改变 solver 的 numeraire 坐标。

## 6. Independent Diagnostics

Diagnostics 从 `Economy + candidate.prices + candidate.allocations` 重新计算需求、预算和市场量，不信任 candidate 缓存的 aggregate demand、aggregate endowment 或 excess demand。

实际严格诊断结果：

| 检查 | 数值误差 | 结果 |
|---|---:|---|
| Numeraire error | `0.0` | PASS |
| Good 1 residual | `0.0` | PASS |
| Good 2 residual | `0.0` | PASS |
| Max market violation | `0.0` | PASS |
| Consumer 1 budget residual | `0.0` | PASS |
| Consumer 2 budget residual | `0.0` | PASS |
| Max budget violation | `0.0` | PASS |
| Max budget exhaustion gap | `0.0` | PASS |
| Consumer 1 optimality gap | `0.0` | PASS |
| Consumer 2 optimality gap | `0.0` | PASS |
| Walras residual `p dot z(p)` | `0.0` | PASS |

最终 classification：

```text
VERIFIED_CANDIDATE
```

错误 candidate 测试人工写入 `solver_success=True` 和缓存 `excess_demand=[0,0]`，但使用 `p=(2,1)` 和错误 allocations。Diagnostics 独立重算得到：

```text
z(p) = [-0.25, 0.5]
p dot z(p) = 0.0
classification = SOLVER_POINT
```

因此测试同时证明：solver success 不能代替均衡验证，Walras law 也不能代替逐市场出清。

## 7. Test Results

最终真实运行：

```text
python -m pytest -q
.......................... [100%]
26 passed in 0.55s
```

覆盖内容：

- Cobb-Douglas demand ground truth；
- 非法 alpha、alpha 不加总、维数错误；
- zero/negative Cobb-Douglas prices 的明确拒绝；
- 财富 `p dot omega`；
- budget residual 的符号；
- FixedNumeraire encode/decode；
- signed L1 符号保持、正比例尺度不变与零向量异常；
- 解析均衡价格与 allocations；
- 两个市场分别出清；
- 非均衡价格下 Walras law 仍成立；
- bracket 无符号变化时返回 `FAILED_RUN`；
- 伪造 solver success 和缓存 residual 的拒绝；
- candidate 缓存向量 shape 错误的拒绝。

其他验证：

```text
python scripts/run_baseline.py   -> exit code 0
python -m compileall src         -> success
python -m pip check              -> No broken requirements found
package import                   -> duanmu_ge_lab 0.1.0
```

验证环境：Python 3.12.13、NumPy 2.5.2、SciPy 1.18.0、pytest 9.1.1。项目元数据声明 Python `>=3.11`。

## 8. Files Created

项目与文档：

- `pyproject.toml`
- `README.md`
- `CITATIONS.md`
- `MILESTONE_1_REPORT.md`
- `docs/analytical_benchmark.md`
- `scripts/run_baseline.py`
- `results/milestone1_baseline.json`

核心包：

- `src/duanmu_ge_lab/__init__.py`
- `src/duanmu_ge_lab/benchmarks.py`
- `src/duanmu_ge_lab/core/{commodity,preferences,consumer,economy}.py`
- `src/duanmu_ge_lab/equilibrium/{candidate,normalization,diagnostics}.py`
- `src/duanmu_ge_lab/solvers/exchange_solver.py`
- 三个非空 package `__init__.py`

测试：

- `tests/test_preferences.py`
- `tests/test_consumer.py`
- `tests/test_price_normalization.py`
- `tests/test_market_clearing.py`
- `tests/test_walras_law.py`
- `tests/test_analytical_equilibrium.py`
- `tests/test_diagnostics_reject_invalid.py`

项目内还生成 `.venv`、pytest cache、Python bytecode 和 editable-install metadata，均位于指定的 `codepart/duanmu_ge_lab` 目录。

## 9. Known Limitations

- Solver 只支持 2 goods、1 个 non-numeraire price 和全部商品 `EXACT` clearing。
- `CobbDouglasUtility.marshallian_demand` 只支持严格正价格；不支持的价格明确抛出 `UnsupportedPriceDomainError`。
- `ClearingRule.FREE_DISPOSAL` 已进入数据与 diagnostics 语义，但本轮 solver 和 benchmark 不使用它。
- 没有生产、企业收入、政府、配额、排放税、坏品专用可行集或外部性。
- 没有多起点、延拓、聚类或多重均衡完备性声明。
- 数值结果只验证当前有限 benchmark，不构成一般存在性或唯一性证明。

## 10. Design Decisions

1. `PreferenceModel` 是抽象接口；Cobb-Douglas 是本轮计算选择。
2. `CommodityKind` 不决定价格符号、单调性、处置或监管。
3. `FixedNumeraire` 与 price-sign restrictions 分离。
4. 没有 softmax；signed L1 函数保留负号，零向量报错。
5. 求解器只求 `z_1=0`；`z_2` 与 Walras law 由 diagnostics 分开检查。
6. Candidate 不保存 `market_clearing_pass` 一类 solver 自证字段。
7. Diagnostics 不使用 candidate 缓存 residual 做判定。
8. 严格容差集中于 `NumericalTolerances`；没有散落的宽松 magic tolerances。
9. bracket 无 sign change 返回失败 candidate，不把数值失败解释为均衡不存在。
10. benchmark 常数只存在于 `benchmarks.py`、benchmark 文档、脚本输出和测试，不泄漏进 `Consumer`、`Economy` 或 solver 通用逻辑。

## 11. Failed Attempts / Bugs Encountered

- 系统普通 `PATH` 中没有 `python` 命令。解决方式：使用 Codex 提供的 Python 3.12.13 创建项目内 `.venv`；README 仍给出普通 Windows Python 3.11+ 安装命令。
- 创建测试文件时，补丁工具第一次没有自动建立 `tests/` 父目录。显式创建该目录后继续，没有丢失文件。
- 第一次完整测试为 `25 passed`。软件自审发现 diagnostics 应同时拒绝 candidate 缓存聚合向量的 shape 错误；补充检查和一个测试后，最终为 `26 passed`。
- 对 `[2,3]` bracket，残差没有 sign change。求解器按设计返回 `FAILED_RUN`，没有 crash；该情形已测试。
- 没有未解决的测试失败或已知运行时 bug。

代码中 `np.maximum.reduce` 只用于构造 diagnostics 的市场误差尺度；`np.abs(price_array)` 只用于任务要求的 signed L1 归一化。没有使用 clipping、绝对值替换价格、epsilon price replacement 或 residual 修补。

## 12. Exact Commands to Reproduce

Windows PowerShell：

```powershell
cd <path-to-project>\duanmu_ge_lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\run_baseline.py
.\.venv\Scripts\python.exe -m compileall src
```

JSON 结果：

```text
<project-root>\results\milestone1_baseline.json
```

## 13. Recommended Milestone 2

按照已批准的 `IMPLEMENTATION_PLAN.md`，下一阶段建议是 Production，但必须由新的任务明确启动。本轮没有创建任何 production 代码。

建议 Milestone 2 首先完成：

1. `Firm` 与 `ProductionTechnology` 的最小接口；
2. 净生产向量与利润最大化；
3. 企业持股和股息进入消费者收入；
4. 资源会计扩展为 `demand - endowment - production`；
5. 一个同样具有解析答案的生产经济 benchmark；
6. 独立 profit-gap 和 ownership-accounting diagnostics。

在进入 Milestone 2 前，最值得交给数学审阅者检查的文件是：

- `docs/analytical_benchmark.md`
- `src/duanmu_ge_lab/equilibrium/diagnostics.py`
- `src/duanmu_ge_lab/solvers/exchange_solver.py`
- `tests/test_diagnostics_reject_invalid.py`
