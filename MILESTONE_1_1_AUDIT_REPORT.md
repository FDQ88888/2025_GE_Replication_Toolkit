# Duanmu GE Lab - Milestone 1.1 Audit Report

> 完成日期：2026-08-09  
> 范围：Milestone 1 诊断架构修复与回归门禁  
> 最终状态：**PASS，可以进入下一独立里程碑**

## 1. 审计结论

本轮修复了一个会改变均衡判定对象的实质性漏洞：旧 diagnostics 用给定价格下重新优化得到的需求检查市场出清，却用 `candidate.allocations` 检查预算与最优性。这样一份报告同时讨论了两个不同配置，可能把资源不可行的候选误写成市场出清。

当前实现严格分离：

```text
候选资源残差       r(x) = sum_i x_i(candidate) - sum_i omega_i
正式 Walras residual     = p dot r(x)
重新优化需求残差   z(p) = sum_i x_i^opt(p) - sum_i omega_i
```

`r(x)` 决定候选市场出清，`p dot r(x)` 是正式候选 Walras 诊断；`z(p)` 只作为重新优化审计信息和消费者最优性参照。

## 2. A1-A7 修复矩阵

| 编号 | 问题 | 修复 | 最终结果 |
|---|---|---|---|
| A1 | 市场出清错误地基于重新优化需求 | 改为基于 `candidate.allocations` 聚合后的 `candidate_resource_residual` | PASS |
| A2 | Walras residual 的对象含糊 | 正式字段改为 `candidate_walras_residual = p dot candidate_resource_residual`；另报 `reoptimized_walras_residual` | PASS |
| A3 | 缺少消费集合可行性 | 增加有限、维数和非负性检查以及 `consumer_feasibility` 硬门禁 | PASS |
| A4 | bundle distance 被当成一般最优性 | 增加 `ConsumerOptimalityResult`，正式判据改为 utility gap；bundle gap 仅标为 `UNIQUE_DEMAND_BENCHMARK_CHECK` | PASS |
| A5 | numeraire 使用浮点精确相等 | `FixedNumeraire.encode` 改用可配置 absolute tolerance 与 `np.isclose`，不修改输入 | PASS |
| A6 | 缺少版本控制排除规则 | 新增 `.gitignore`，排除本地环境、缓存、构建和 coverage 产物 | PASS |
| A7 | 缺少针对上述漏洞的门禁 | 新增 6 个审计相关测试；完整测试由 26 增至 32 | PASS |

## 3. 数学影响与新旧行为

### 3.1 候选资源可行性

旧行为：给定 `candidate.prices` 后重新求需求，并用该需求聚合量判断市场，因此没有真正检查候选 allocations 是否可行。

新行为：只用候选 allocations 与经济的真实总禀赋形成市场 residual。candidate 内缓存的 aggregate demand、aggregate endowment 和 excess demand 不参与判定。

关键回归取：

```text
p = (1,1)
x_1(candidate) = x_2(candidate) = (0.8,0.2)
x_1^opt(p) = x_2^opt(p) = (0.5,0.5)
```

得到：

```text
candidate_resource_residual = (0.6,-0.6)
reoptimized_resource_residual = (0,0)
candidate_walras_residual = 1.11e-16 约等于 0
market_clearing = false
consumer_optimality = false
```

这证明重新优化需求出清不能替代候选资源可行性，也证明 Walras residual 为零不能替代逐市场检查。

### 3.2 消费集合

当前 Milestone 1 的消费集合是 `R_+^L`。回归候选

```text
x_1=(-0.1,1.1), x_2=(1.1,-0.1)
```

在总量上恰好等于总禀赋、预算也恰好耗尽，但每个消费者都有 `0.1` 的非负性违反。新 diagnostics 因此给出：

```text
market_clearing = true
budget_feasibility = true
consumer_feasibility = false
consumer_optimality = false
passed = false
```

### 3.3 最优性架构

新增 `ConsumerOptimalityResult`，至少报告：

- `feasible`；
- `candidate_utility`；
- `optimal_utility`；
- `utility_gap`；
- `budget_violation`；
- `method`。

另报告消费集合违反量和仅适用于唯一需求 benchmark 的 bundle gap。正式 `consumer_optimality` 使用 `abs(utility_gap)` 与集中容差比较，不要求候选 bundle 与某一个最优 bundle 完全相同，因此接口允许未来处理多重最优解。

当前支持范围是具有数值效用函数和可验证 Marshallian-demand oracle 的 `PreferenceModel`。尚未转化为数值效用/优化问题的论文 relation-only preference 明确标记为 `UNSUPPORTED_UTILITY_OPTIMALITY_ORACLE`，不会猜测或自动通过。

### 3.4 Numeraire

`FixedNumeraire(index, value, tolerance)` 现在接受绝对误差不超过 tolerance 的输入，超出时抛出包含期望值、容差、实际值和“不修改输入”说明的错误。实现没有 rounding、clipping 或静默替换价格。

## 4. 报告字段

当前 JSON 使用以下无歧义字段：

```text
candidate_aggregate_allocation
candidate_resource_residual
candidate_walras_residual
reoptimized_allocations
reoptimized_resource_residual
reoptimized_walras_residual
consumer_feasibility_violations
utility_gaps
unique_demand_bundle_gaps
consumer_optimality_results
```

Python report 暂时保留 `market_residuals`、`walras_residual`、`recomputed_allocations` 和 `optimality_gaps` 只读兼容别名，但它们不再出现在新 JSON 中，项目代码也不再使用这些含糊名称。

## 5. 回归测试

新增或扩展的测试覆盖：

1. 候选 allocations 不出清、重新优化需求出清时，必须拒绝候选；
2. 正式 candidate Walras residual 与 reoptimized Walras residual 明确分开；
3. 负消费即便满足总资源与预算，也必须拒绝；
4. 结构化 utility-gap 最优性结果及唯一需求标签；
5. numeraire 在容差内接受且不修改输入；
6. numeraire 在容差外明确报错。

原先 `p=(2,1)` 的伪造 candidate 测试也已修正语义：其候选 allocations 总量恰好出清，所以 `candidate_resource_residual=(0,0)`；但预算和效用最优性失败。独立重新优化需求的 residual 才是 `(-0.25,0.5)`。

## 6. 最终验证结果

最终实际运行：

```text
.venv\Scripts\python.exe -m pytest -q
................................ [100%]
32 passed in 0.55s
```

基准运行：

```text
.venv\Scripts\python.exe scripts\run_baseline.py
classification = VERIFIED_CANDIDATE
candidate_resource_residual = [0.0,0.0]
candidate_walras_residual = 0.0
utility_gaps = {Consumer 1: 0.0, Consumer 2: 0.0}
exit code = 0
```

其他门禁：

```text
python -m compileall -q src -> exit code 0
python -m pip check          -> No broken requirements found
```

第一次新增回归运行曾有 1 个失败：测试用 `== 0.0` 比较理论零值，而实际浮点结果为 `1.11e-16`。修复的是测试断言（改为 `abs=1e-14`），没有截断或修改经济 residual；随后完整测试全绿。

## 7. 文件与环境卫生

`.gitignore` 排除：

```text
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
build/
dist/
.coverage
htmlcov/
```

本地 `.venv` 可以继续保留用于 VS Code 和测试，但不得提交或分发。本轮没有删除或移动任何源代码、测试、结果或研究文档，所有修改均位于用户指定的 `codepart/duanmu_ge_lab`。

## 8. 残余边界

- utility gap 的绝对容差仍依赖效用表示的尺度；进入异质效用模型前应设计尺度稳健的绝对/相对判据。
- 当前 oracle 是 Cobb-Douglas 闭式 Marshallian demand；它验证的是该可计算 benchmark，不代表已经支持论文的一般 preference relation。
- `FREE_DISPOSAL` 已有逐商品 residual 语义，但尚无相应生产/坏品 benchmark。
- candidate 缓存仍只检查 shape 与有限性，不作为数学判定依据。

上述边界均已显式记录，不影响 Milestone 1.1 当前 benchmark 的通过结论。
