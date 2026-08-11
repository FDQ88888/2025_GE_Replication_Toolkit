# Milestone 1 Analytical Benchmark

## 1. 目的

本 benchmark 用一个精确答案已知的 2 consumers x 2 goods 交换经济，验证如下计算链：

```text
endowments -> wealth -> individual demand -> aggregate excess demand
-> price normalization -> scalar root -> candidate -> independent diagnostics
```

它是 `SOFTWARE VALIDATION BENCHMARK`，不是 Anderson-Duanmu 论文复现。

## 2. 经济

有两种普通商品和两个消费者。所有市场都要求 `EXACT` clearing。

消费者 1 的禀赋和效用为

```text
omega_1 = (1, 0),
u_1(x_11,x_12) = x_11^(1/2) x_12^(1/2).
```

消费者 2 的禀赋和效用为

```text
omega_2 = (0, 1),
u_2(x_21,x_22) = x_21^(1/2) x_22^(1/2).
```

价格为 `p=(p_1,p_2)`。选择第二种商品作为 numeraire：

```text
p_2 = 1.
```

这是数值坐标选择，不是整个项目永久采用的理论假设。

## 3. Cobb-Douglas Marshallian Demand

对效用

```text
u(x_1,x_2) = x_1^alpha x_2^(1-alpha)
```

和预算约束

```text
p_1 x_1 + p_2 x_2 <= w,
```

当 `p_1,p_2>0` 且 `0<alpha<1` 时，内部最优解把 `alpha` 份额的财富用于商品 1，把 `1-alpha` 份额用于商品 2：

```text
x_1 = alpha w / p_1,
x_2 = (1-alpha) w / p_2.
```

本 benchmark 中两个消费者都有 `alpha=1/2`。

## 4. 财富与个体需求

财富按禀赋的市场价值计算：

```text
w_i(p) = p dot omega_i.
```

消费者 1：

```text
w_1 = p_1,
x_11 = (1/2) p_1 / p_1 = 1/2,
x_12 = (1/2) p_1 / p_2 = p_1/2.
```

消费者 2：

```text
w_2 = p_2 = 1,
x_21 = (1/2) / p_1,
x_22 = (1/2) / p_2 = 1/2.
```

## 5. 商品 1 市场与相对价格

商品 1 的总需求为

```text
X_1(p_1,1) = 1/2 + 1/(2p_1).
```

总禀赋为

```text
Omega_1 = 1.
```

全项目固定超额需求符号：

```text
z(p) = aggregate demand - aggregate endowment.
```

所以

```text
z_1(p_1,1) = -1/2 + 1/(2p_1).
```

精确出清要求 `z_1=0`：

```text
-1/2 + 1/(2p_1) = 0,
p_1 = 1.
```

由于 `p_2=1`，解析均衡价格是

```text
p* = (1,1).
```

## 6. 均衡配置

把 `p_1=p_2=1` 代回需求：

```text
x_1* = (1/2,1/2),
x_2* = (1/2,1/2).
```

## 7. 独立检查商品 2

商品 2 总需求为

```text
X_2(p_1,1) = p_1/2 + 1/2.
```

总禀赋 `Omega_2=1`，因此

```text
z_2(p_1,1) = (p_1-1)/2.
```

在 `p_1=1` 时：

```text
z_2(1,1) = 0.
```

求解器没有使用这个方程寻找 `p_1`；它由 diagnostics 独立重算并检查。

## 8. Walras Law

在任意正 `p_1` 下：

```text
p dot z(p)
= p_1[-1/2 + 1/(2p_1)] + [(p_1-1)/2]
= (-p_1/2 + 1/2) + (p_1/2 - 1/2)
= 0.
```

这个例子清楚说明 Walras law 可以在市场尚未逐个出清时成立。例如 `p=(2,1)` 时，`z_1=-1/4`、`z_2=1/2`，但 `p dot z=0`。

因此必须区分：

1. **SOLVED MARKET CONDITION**：求解 `z_1(p_1,1)=0`；
2. **UNUSED MARKET CLEARING CHECK**：独立检查 `z_2(p_1,1)=0`；
3. **WALRAS LAW CHECK**：独立报告 `p dot z(p)`。

Walras law 不能替代逐商品 market diagnostics，也不能被用来修改 residual。

## 9. 自动测试 Ground Truth

测试采用：

```text
p* = [1.0, 1.0]
allocations* = [
  [0.5, 0.5],
  [0.5, 0.5]
]
aggregate demand = [1.0, 1.0]
aggregate endowment = [1.0, 1.0]
z(p*) = [0.0, 0.0]
p* dot z(p*) = 0.0
```

数值 solver 的输出只有在独立 diagnostics 同时验证价格规范、预算、个体最优性、两个市场和 Walras law 后，才可分类为 `VERIFIED_CANDIDATE`。

## 10. 候选配置与重新优化需求必须分离

`z(p)` 是给定价格后重新求解消费者问题得到的超额需求，它用于求解价格和检查需求系统。验证一个具体候选 `(p,x)` 时，市场可行性却必须使用候选配置本身：

```text
r(x) = sum_i x_i - sum_i omega_i,
formal candidate Walras residual = p dot r(x).
```

例如在 `p=(1,1)` 下伪造

```text
x_1 = x_2 = (0.8,0.2).
```

重新优化需求仍为 `(0.5,0.5)`，因而 `z(p)=(0,0)`；但候选资源残差是

```text
r(x) = (0.6,-0.6),
p dot r(x) = 0.
```

所以该候选既不满足逐商品市场出清，也不是消费者最优配置。这个反例同时说明，即便正式候选 Walras residual 为零，也不能推出各市场出清。

消费者最优性采用效用差

```text
utility_gap_i = u_i(x_i^opt) - u_i(x_i^candidate),
```

其中 `x_i^opt` 由预算约束与消费集合下的独立 Marshallian-demand oracle 给出。Cobb-Douglas benchmark 的最优需求唯一，因此额外报告 bundle distance，但它只叫 `UNIQUE_DEMAND_BENCHMARK_CHECK`，不作为一般偏好下的正式判据。当前验证器只支持带数值效用和有效优化 oracle 的偏好；论文中尚未计算化的 relation-only preference 明确属于 unsupported。
