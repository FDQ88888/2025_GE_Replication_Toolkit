# Duanmu GE Lab - Milestone 3 Report

> 完成日期：2026-08-10  
> 范围：Finite Weighted Economies  
> 状态：**PASS**

## 1. 实现结论

`Consumer` 新增严格正且有限的 `population_weight`。该权重只进入经济聚合：

```text
X = sum_i lambda_i x_i,
E = sum_i lambda_i e_i.
```

消费者预算、效用和人均禀赋不乘人口权重。核心模型没有 social welfare weight 字段；未来福利模块必须使用独立对象，因此代码层和文档层都保持：

```text
population weights != welfare weights.
```

## 2. 加权持股

在有限加权生产经济中，`theta_ij` 是持股密度。企业持股和分红会计改为：

```text
sum_i lambda_i theta_ij = 1,
sum_i lambda_i theta_ij pi_j = pi_j.
```

`FirmOwnership` 保留输入的原始 density 数字，不静默归一化。context-free 的普通 share 数字和仅作为 raw debugging statistic；正式 adding-up 由 `ProductionEconomy` 使用 population weights 计算。

当所有 `lambda_i=1` 时，新公式退化为 Milestone 2 的普通有限消费者持股会计，因此既有 production benchmark 不变。

## 3. Split-Agent Invariance Benchmark

原经济有一个类型：

```text
lambda=1, e=(2,0), theta=1.
```

拆分经济用两个完全相同的类型替代：

```text
lambda_A=0.4, lambda_B=0.6,
e_A=e_B=(2,0),
theta_A=theta_B=1.
```

拆分后原始 ownership 字典数字和为 `2`，但正式加权持股总量是 `0.4+0.6=1`。两个经济使用相同生产技术、偏好和 numeraire。

## 4. 实验结果

`scripts/run_weighted_invariance.py` 实际得到：

```text
original prices = [0.33333333333333454, 1.0]
split prices    = [0.33333333333333454, 1.0]

original aggregate allocation
= [1.4999999999999973, 0.5000000000000009]

split aggregate allocation
= [1.4999999999999973, 0.5000000000000009]

original classification = VERIFIED_CANDIDATE
split classification    = VERIFIED_CANDIDATE
```

全部不变量距离：

| 对象 | L2 distance |
|---|---:|
| prices | `0.0` |
| weighted aggregate allocations | `0.0` |
| weighted aggregate endowments | `0.0` |
| firm plans | `0.0` |
| firm profits | `0.0` |
| candidate resource residuals | `0.0` |

结果保存在 `results/milestone3_split_agent_invariance.json`。

## 5. 自动测试

新增测试覆盖：

- zero、negative、NaN、infinite population weight 拒绝；
- 原经济与拆分经济的加权禀赋一致；
- 原始 shares 和与加权 ownership total 的明确区分；
- 两个经济独立求解并独立通过 diagnostics；
- 价格、聚合配置、生产、利润和 residual 全部保持。

完整测试在实现后达到：

```text
44 passed in 0.60s
```

## 6. 修改范围

- `Consumer.population_weight`；
- `ExchangeEconomy` 与 `ProductionEconomy` 的加权聚合；
- production ownership/dividend diagnostics 的加权 adding-up；
- exchange/production solver 缓存统一使用 economy aggregate API；
- `build_split_agent_invariance_benchmarks()`；
- `tests/test_weighted_economy.py`；
- `scripts/run_weighted_invariance.py`；
- `docs/finite_weighted_economies.md`。

## 7. 研究边界

- 本里程碑验证有限原子质量会计，不是 continuum economy。
- Split-agent invariance 是结构回归，不是测度收敛、weak convergence 或 Loeb measure 证明。
- 当前权重不用于社会福利汇总；welfare 模块尚未实现。
- 没有抽样、类型分区、尾部吸收或大经济规模扫描。

Milestone 3 只有在完整测试、M1/M2/M3 实验、编译与依赖检查全部通过后才正式关闭。
