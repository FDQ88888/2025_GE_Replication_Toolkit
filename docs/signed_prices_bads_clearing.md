# Signed Prices, Bads, and Clearing Rules

## 1. 三个独立对象

本项目严格分离：

1. `CommodityKind`：GOOD/BAD 语义元数据；
2. `PriceSignRestrictions`：经济规格显式给出的价格符号区域；
3. `ClearingRule`：逐商品 exact clearing 或 free disposal。

`CommodityKind.BAD` 不自动推出负效用、负价格、政府监管、固定零消费或自由处置。

## 2. 归一化不是符号限制

`normalize_signed_l1(p)` 只做：

```text
p -> p / sum_l |p_l|.
```

它保留每个坐标的符号。`rescale_to_fixed_numeraire` 只允许正比例缩放；若目标 numeraire 需要负比例翻转全部符号，函数明确拒绝。

对于 benchmark：

```text
fixed-numeraire p=(-1,1),
signed-L1 p=(-1/2,1/2).
```

往返误差为零。代码没有 softmax、`abs(price)`、clipping 或 epsilon replacement。

## 3. 消费集合决定坏品吸收

默认消费集合是 `NonnegativeOrthant`。`BoxConsumptionSet` 可以逐坐标给定上下界，包括：

- bad absorption 上限；
- 某论文例子的 fixed-zero 坐标；
- 普通商品的非负无上界坐标。

这些约束来自消费者规格，不来自 commodity kind。

## 4. 负价坏品解析 Benchmark

一个消费者有禀赋：

```text
e=(b,g)=(1,2).
```

消费集合和效用是：

```text
0<=b<=1,
g>=0,
u(b,g)=g-(1/2)b.
```

在 `p=(-1,1)` 下，财富为 `p dot e=1`。预算是：

```text
-b+g<=1,
g<=1+b.
```

代入效用上界：

```text
u<=1+b-(1/2)b=1+(1/2)b.
```

所以消费者唯一选择最大吸收量 `b=1`，并消费 `g=2`。候选配置等于总禀赋，两个商品都 exact clear，utility gap、预算 residual、资源 residual 与 Walras residual 均为零。

这个例子说明负价格可为吸收坏品提供补偿，但它不是 Anderson-Duanmu 论文例子，也不声称所有坏品都必须有负价格。

## 5. Exact 与 Free Disposal

项目 residual 统一为 demand/allocation minus available resources。

```text
EXACT: residual_l = 0,
FREE_DISPOSAL: residual_l <= 0.
```

测试用同一候选 residual `(-0.5,0)` 验证：第一商品设为 FREE_DISPOSAL 时 market check 通过，设为 EXACT 时失败。没有额外添加 generic complementarity；以后 paper-specific compliance region 必须按原文定义单独实现。
