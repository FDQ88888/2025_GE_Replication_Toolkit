# Milestone 2 Analytical Production Benchmark

## 1. 学术身份

这是 `ANALYTICAL PRODUCTION BENCHMARK`，用于验证企业、净产出、持股分红、消费者总收入与候选资源会计。它是 `OUR COMPUTATIONAL CHOICE`，不是 Anderson-Duanmu 论文复现。

## 2. 经济与技术

两种普通商品、两个消费者和一个企业。两个市场都要求精确出清。每个消费者有禀赋

```text
e_1=e_2=(1,0)
```

和效用

```text
u_i(x_i)=x_i1^(1/2) x_i2^(1/2).
```

企业采用净产出约定：正坐标是 output，负坐标是 input。生产集合是

```text
Y={a(-1,1): 0<=a<=1/2}.
```

消费者 1 和 2 的持股分别是 `1/4` 与 `3/4`。第二种商品是 numeraire：`p_2=1`。令 `p_1=q`。

## 3. 企业最优性

活动水平 `a` 的利润是

```text
pi(a;q)=p dot y=a(1-q).
```

当 `0<q<1` 时单位利润严格为正，因此唯一最优活动是容量上界：

```text
a*=1/2,
y*=(-1/2,1/2),
pi*=(1-q)/2.
```

基准求根 bracket `[0.1,0.8]` 完全位于这一解析分支内。它是 benchmark-specific 的数值设置，不是通用生产经济假设。

## 4. 收入拆分

无政策生产经济的消费者收入为

```text
I_i=p dot e_i+theta_i*pi.
```

所以

```text
I_1=q+(1/4)(1-q)/2=(7q+1)/8,
I_2=q+(3/4)(1-q)/2=(5q+3)/8.
```

总收入等于总可用资源的价值：

```text
I_1+I_2=(3q+1)/2
          =p dot [(2,0)+(-1/2,1/2)].
```

## 5. 市场方程

Cobb-Douglas 需求为

```text
x_i1=(1/2)I_i/q,
x_i2=(1/2)I_i.
```

净生产后的总可用资源是

```text
sum_i e_i+y*=(3/2,1/2).
```

商品 1 聚合需求为

```text
X_1(q)=(1/2)(I_1+I_2)/q=(3q+1)/(4q).
```

令 `X_1(q)=3/2`：

```text
(3q+1)/(4q)=3/2,
3q+1=6q,
q=1/3.
```

因此解析均衡价格为

```text
p*=(1/3,1).
```

## 6. 利润、分红与配置

在解析价格下：

```text
pi*=1/3,
dividend_1=(1/4)(1/3)=1/12,
dividend_2=(3/4)(1/3)=1/4,
I_1=5/12,
I_2=7/12.
```

消费者配置为

```text
x_1*=(5/8,5/24),
x_2*=(7/8,7/24).
```

聚合配置是 `(3/2,1/2)`，恰好等于总禀赋加净生产。

## 7. 候选资源与 Walras 诊断

正式候选资源 residual 只使用候选 `(x,y)`：

```text
r(x,y)=sum_i x_i-sum_i e_i-sum_j y_j.
```

在解析配置处 `r=(0,0)`，正式候选 Walras residual `p dot r=0`。企业和消费者最优性分别由独立利润 oracle 和独立效用 oracle 检查，不能由市场出清替代。

## 8. 验收对象

自动测试与实验同时核对：

- 企业生产集合可行性；
- 全局最大利润与 `profit_gap`；
- 持股和为 1；
- 分红合计等于企业利润；
- 消费者预算与 utility gap；
- `consumption - endowment - net production`；
- 未用于求根的第二市场；
- 正式 candidate Walras residual；
- 数值结果与全部解析分数一致。
