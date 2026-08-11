# Finite Weighted Economies

## 1. 两种权重不能混用

`population_weight`（记为 `lambda_i`）是消费者类型或原子的经济质量。它只进入 paper-defined aggregate quantities：

```text
aggregate consumption = sum_i lambda_i x_i,
aggregate endowment   = sum_i lambda_i e_i.
```

社会福利权重用于研究者额外选择的 welfare aggregator。它不进入资源约束、市场出清、企业利润或消费者预算。当前核心模型没有 social-welfare-weight 字段；未来福利模块必须使用另一个明确命名的数据结构。

```text
population weights != social welfare weights.
```

## 2. 人均对象与聚合对象

`Consumer.endowment`、消费 bundle 和收入都是该类型的人均对象。人口权重不乘入个体预算：

```text
individual income_i = p dot e_i + sum_j theta_ij pi_j.
```

只有将个体对象加总为经济总量时才乘 `lambda_i`。权重必须有限且严格为正。核心允许总质量不是 1；是否归一化为概率质量由具体经济规格决定。

## 3. 加权持股密度

在加权经济中，`theta_ij` 按持股密度解释。每个企业的 adding-up condition 是：

```text
sum_i lambda_i theta_ij = 1.
```

因此不能仅计算字典中 share 数字的普通和，也不能自动归一化 shares。企业分红的聚合会计是：

```text
sum_i lambda_i theta_ij pi_j = pi_j.
```

当所有 `lambda_i=1` 时，这退化为 Milestone 2 的普通有限消费者 shares adding-up。

## 4. Split-Agent Invariance

原经济有一个消费者类型：

```text
lambda=1,
e=(2,0),
theta=1.
```

拆分经济用两个完全相同的类型替代它：

```text
lambda_A=0.4,
lambda_B=0.6,
e_A=e_B=(2,0),
theta_A=theta_B=1.
```

于是：

```text
lambda_A+lambda_B=1,
lambda_A theta_A+lambda_B theta_B=1.
```

两个类型的人均需求相同，故加权总需求、总禀赋、持股利润、企业计划、均衡价格与资源 residual 应与原经济相同。注意 split ownership 字典中的原始数字和是 2，但正确的加权持股总量是 1。

## 5. 验收标准

原经济与拆分经济都必须独立得到 `VERIFIED_CANDIDATE`，且以下距离低于严格容差：

- price distance；
- weighted aggregate allocation distance；
- weighted aggregate endowment distance；
- firm plan 与 profit distance；
- candidate resource residual distance。

该不变量是有限加权聚合实现的结构测试，不是测度经济收敛或 Loeb measure 的数值证明。
