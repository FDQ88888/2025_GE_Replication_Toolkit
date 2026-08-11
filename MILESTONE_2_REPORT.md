# Duanmu GE Lab - Milestone 2 Report

> 完成日期：2026-08-10  
> 范围：Production Economy  
> 状态：**PASS**；尚未进入 quota、emission tax 或 paper replication

## 1. 本轮目标

Milestone 2 把经过 M1.1 审计的交换经济扩展为无政策的有限生产经济。核心不变量是：

```text
candidate_resource_residual
= sum_i candidate.x_i
  - sum_i e_i
  - sum_j candidate.y_j.
```

企业使用 net-output convention：正坐标为 output，负坐标为 input。市场出清只使用候选 `(x,y)`；消费者和企业最优性分别由独立效用与利润 oracle 重算。

## 2. 新增数学对象

- `ProductionTechnology`：生产集合与全局利润 oracle 的抽象接口；
- `CapacityConstrainedLinearTechnology`：`Y={a*v:0<=a<=capacity}` 的解析 benchmark 技术；
- `Firm`：企业 id、技术和持股；
- `FirmOwnership`：保留原始 shares，不做静默归一化；
- `IncomeBreakdown`：endowment income、firm dividend income、policy income 和 total income；
- `ProductionEconomy`：企业、持股、需求、利润、收入与 `x-e-y` 资源会计；
- `ProductionEquilibriumCandidate`：只记录 solver point，不携带验证结论；
- `ProductionEquilibriumDiagnostics`：独立重算所有生产经济条件；
- `ProductionEquilibriumSolver`：只服务于两商品解析 benchmark 的 Brent 标量求根器。

`policy_income` 在本里程碑恒为零，只是显式收入坐标；本轮没有实现任何政策规则。

## 3. 解析生产 Benchmark

本 benchmark 标记为 `ANALYTICAL_PRODUCTION_BENCHMARK` 和 `OUR COMPUTATIONAL CHOICE`，不是 Anderson-Duanmu paper replication。

两个消费者都有：

```text
e_i=(1,0),
u_i(x)=x_i1^(1/2)x_i2^(1/2).
```

企业生产集合与持股是：

```text
Y={a(-1,1):0<=a<=1/2},
theta_1=1/4,
theta_2=3/4.
```

固定 `p_2=1` 并令 `p_1=q`。在 benchmark bracket `q in [0.1,0.8]` 内，企业单位利润 `1-q>0`，所以唯一最优计划为容量生产：

```text
y*=(-1/2,1/2),
pi*=(1-q)/2.
```

把持股利润纳入两个消费者收入后，商品 1 市场方程给出：

```text
(3q+1)/(4q)=3/2,
q=1/3.
```

完整解析解：

```text
p*=(1/3,1)
y*=(-1/2,1/2)
pi*=1/3

I_1=endowment 1/3 + dividend 1/12 = 5/12
I_2=endowment 1/3 + dividend 1/4  = 7/12

x_1*=(5/8,5/24)
x_2*=(7/8,7/24)
```

完整推导见 `docs/analytical_production_benchmark.md`。

## 4. 独立 Diagnostics

Production diagnostics 的硬检查包括：

1. solver success；
2. 候选和全部缓存的 shape/有限性；
3. numeraire；
4. 每个企业持股和为 1；
5. 企业生产集合可行性；
6. 企业利润 oracle 可用；
7. candidate profit 与独立最大利润的 gap；
8. 分红合计与企业利润对账；
9. 消费集合可行性；
10. 候选预算可行性；
11. 消费者效用 oracle 可用；
12. utility gap；
13. solver cache 与独立重算量一致；
14. 逐商品候选资源出清；
15. 正式 candidate Walras residual。

预算 exhaustion 另行报告，但不在一般生产经济中无条件作为硬假设。所有容差集中在 `NumericalTolerances`，新增 production feasibility、profit、ownership 和 accounting 四类阈值。

## 5. 数值结果

实际运行 `scripts/run_production_baseline.py` 得到：

```text
prices       = [0.33333333333333454, 1.0]
firm plans   = [[-0.5, 0.5]]
firm profits = [0.3333333333333327]
classification = VERIFIED_CANDIDATE
```

解析距离：

| 对象 | L2 distance |
|---|---:|
| prices | `1.22124532708767e-15` |
| allocations | `2.29835607586495e-15` |
| firm plans | `0.0` |
| firm profits | `6.10622663543836e-16` |

诊断误差：

| 诊断 | 最大误差 |
|---|---:|
| ownership adding-up | `0.0` |
| firm feasibility | `0.0` |
| profit gap | `0.0` |
| dividend accounting | `0.0` |
| consumer feasibility | `0.0` |
| budget violation/exhaustion | `0.0` |
| utility gap | `0.0` |
| candidate cache consistency | `0.0` |
| market violation | `2.66453525910038e-15` |
| candidate Walras residual | `3.15544362088405e-30` |

结果保存在：

```text
results/milestone2_production_baseline.json
```

## 6. 关键回归测试

- 已知全局企业最优计划与利润；
- 超容量计划的生产集合违反；
- 负利润 margin 时企业关停；
- 持股 `0.4+0.4` 保持为 `0.8`，绝不被归一化；
- 分红收入 `1/12` 与 `1/4`；
- `sum x = sum e + sum y`；
- 求解器恢复全部解析解；
- 一个 `y=0` 的候选可以恰好市场出清，但因 firm profit gap `1/3` 和 consumer utility gap 被拒绝；
- 持股不加总时 ownership 与 dividend accounting 同时失败；
- 嵌套 income cache 含 `NaN` 时，finite-values 与 cache-consistency 硬门禁拒绝候选。

## 7. 测试与验证

最终测试门禁：

```text
.venv\Scripts\python.exe -m pytest -q
......................................... [100%]
41 passed in 0.57s
```

Milestone 2 初次全套运行曾出现 `1 failed, 39 passed`：通用 `Consumer` 层过早拒绝负收入，使旧负价格测试收到收入域错误而不是 Cobb-Douglas 的价格域错误。修复后，通用层只检查总收入有限性，负收入是否支持由具体 preference oracle 决定；预算诊断仍可计算负收入。这一修复为未来企业亏损按持股传递保留了正确边界。

随后自审发现嵌套 income cache 的 `NaN` 风险，增加有限性门禁与回归后达到 41 项测试。没有通过 clipping、改 residual 或放宽数学容差修复测试。

## 8. 文件清单

核心：

```text
src/duanmu_ge_lab/core/income.py
src/duanmu_ge_lab/core/production.py
src/duanmu_ge_lab/core/production_economy.py
src/duanmu_ge_lab/equilibrium/production_diagnostics.py
src/duanmu_ge_lab/solvers/production_solver.py
```

实验与说明：

```text
scripts/run_production_baseline.py
docs/analytical_production_benchmark.md
results/milestone2_production_baseline.json
MILESTONE_2_REPORT.md
```

测试：

```text
tests/test_production.py
tests/test_production_equilibrium.py
```

## 9. 研究边界

- 当前技术是有界单活动线性集合，不代表通用非线性或无界生产对应已经求解。
- 当前 production solver 只支持 2 goods、1 个独立价格和全部市场 exact clearing。
- Cobb-Douglas demand 仍只支持严格正价格；signed-price 经济将在独立里程碑处理。
- 企业亏损可按 signed profit 进入收入会计，但本 benchmark 不产生亏损。
- 没有政府企业、quota rights、tax revenue、rebate rule 或 externality state。
- 没有实现 Anderson-Duanmu Example 1；官方 Supplement 已取得，但必须先用后续 quota 模块表达原文 Definition 3.1-3.5。

## 10. Gate 结论

Milestone 2 的解析解、solver、企业最优性、持股收入、候选资源会计、独立 diagnostics、负例和可复现实验均已完成。只有最终全套测试、M1/M2 脚本、compileall 和 pip check 再次全绿后，才允许进入 Milestone 3。
