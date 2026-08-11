# Duanmu GE Lab - Milestone 4 Report

> 完成日期：2026-08-10  
> 范围：Signed Prices, Bads, Clearing Rules  
> 状态：**PASS**

## 1. 实现内容

- `PriceSign` 与逐坐标 `PriceSignRestrictions`；
- signed L1 与 fixed-numeraire 的正比例往返转换；
- `ConsumptionSet`、`NonnegativeOrthant`、`BoxConsumptionSet`；
- `BadAbsorptionLinearUtility` 的负价解析 demand oracle；
- diagnostics 中独立的 price-normalization 与 price-sign 硬检查；
- exact/non-free-disposal 坏品 benchmark；
- free-disposal 与 exact-clearing 对照回归。

所有对象都保持以下不变量：

```text
commodity semantic kind
!= price sign restriction
!= consumption feasibility
!= clearing rule.
```

## 2. Signed Price 处理

价格限制可选 `ANY`、`NONNEGATIVE`、`NONPOSITIVE`、`POSITIVE`、`NEGATIVE` 或 `ZERO`。限制由经济规格显式传入 diagnostics；商品 BAD 标签不创建默认限制。

`normalize_signed_l1` 保留符号，`rescale_to_fixed_numeraire` 只允许正比例。测试确认：

```text
(-2,1) -> (-2/3,1/3) -> (-2,1).
```

试图用负比例得到相反符号的 numeraire 会明确报错。

## 3. 坏品吸收 Benchmark

benchmark 是软件验证选择，不是论文复现：

```text
e=(1 bad, 2 good),
X=[0,1] x R_+,
u(b,g)=g-b/2,
p=(-1,1),
x*=(1,2).
```

正式结果：

```text
fixed-numeraire prices = [-1,1]
signed-L1 prices       = [-0.5,0.5]
candidate residual     = [0,0]
candidate Walras       = 0
classification         = VERIFIED_CANDIDATE
```

消费上限由 `BoxConsumptionSet` 实施；候选 bad consumption `1.1` 的 feasibility violation 是 `0.1`。

## 4. Clearing Rule 回归

对 candidate residual `(-0.5,0)`：

- 第一商品 `FREE_DISPOSAL`：market clearing check 通过；
- 第一商品 `EXACT`：market clearing check 失败。

该测试只验证逐商品资源区域，不添加未由模型定义的 complementarity 条件。

## 5. 测试结果

新增测试覆盖：

- signed L1/numeraire round trip；
- 负比例缩放拒绝；
- BAD 标签不隐含负价；
- 负价坏品 verified candidate；
- bounded bad absorption；
- exact 与 free-disposal 的不同判定。

实现后完整测试：

```text
50 passed in 0.49s
```

## 6. 文件与输出

```text
src/duanmu_ge_lab/core/consumption.py
src/duanmu_ge_lab/equilibrium/prices.py
tests/test_signed_prices_and_bads.py
scripts/run_signed_bad_baseline.py
docs/signed_prices_bads_clearing.md
results/milestone4_signed_bad_absorption.json
MILESTONE_4_REPORT.md
```

## 7. 研究边界

- 当前负价 preference 是两坐标解析 benchmark，不是通用不完备偏好。
- 当前 benchmark 没有生产副产品、封存、外部性或政策。
- `FREE_DISPOSAL` 只实现定义中的 residual inequality，没有自动互补条件。
- Anderson-Duanmu 的 `Z(m)` 与 emission-tax compliance region 尚未实现；它们必须在政策里程碑按原文单独定义。

M4 只有在全部旧/新测试、四套实验、编译和依赖检查全绿后才关闭。
