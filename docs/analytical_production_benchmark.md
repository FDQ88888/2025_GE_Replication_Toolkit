# Milestone 2 Analytical Production Benchmark

## 1. Research Status

This `ANALYTICAL PRODUCTION BENCHMARK` validates firms, net output, ownership dividends, total consumer income, and candidate resource accounting. It is `OUR COMPUTATIONAL CHOICE`, not a replication of the Anderson-Duanmu paper.

## 2. Economy and Technology

There are two ordinary goods, two consumers, and one firm. Both markets require exact clearing. Each consumer has endowment

```text
e_1=e_2=(1,0)
```

and utility

```text
u_i(x_i)=x_i1^(1/2) x_i2^(1/2).
```

The firm follows the net-output convention: positive coordinates are outputs and negative coordinates are inputs. Its production set is

```text
Y={a(-1,1): 0<=a<=1/2}.
```

Consumers 1 and 2 own shares `1/4` and `3/4`, respectively. Good 2 is the numeraire: `p_2=1`. Let `p_1=q`.

## 3. Firm Optimality

Profit at activity level `a` is

```text
pi(a;q)=p dot y=a(1-q).
```

When `0<q<1`, unit profit is strictly positive, so the unique optimal activity is the capacity bound:

```text
a*=1/2,
y*=(-1/2,1/2),
pi*=(1-q)/2.
```

The benchmark root bracket `[0.1,0.8]` lies entirely within this analytical branch. This is a benchmark-specific numerical setting, not a general assumption about production economies.

## 4. Income Decomposition

In a production economy without policy, consumer income is

```text
I_i=p dot e_i+theta_i*pi.
```

Therefore,

```text
I_1=q+(1/4)(1-q)/2=(7q+1)/8,
I_2=q+(3/4)(1-q)/2=(5q+3)/8.
```

Total income equals the value of aggregate available resources:

```text
I_1+I_2=(3q+1)/2
          =p dot [(2,0)+(-1/2,1/2)].
```

## 5. Market Equation

Cobb-Douglas demands are

```text
x_i1=(1/2)I_i/q,
x_i2=(1/2)I_i.
```

Aggregate resources available after net production are

```text
sum_i e_i+y*=(3/2,1/2).
```

Aggregate demand for good 1 is

```text
X_1(q)=(1/2)(I_1+I_2)/q=(3q+1)/(4q).
```

Setting `X_1(q)=3/2` gives:

```text
(3q+1)/(4q)=3/2,
3q+1=6q,
q=1/3.
```

Hence the analytical equilibrium price is

```text
p*=(1/3,1).
```

## 6. Profit, Dividends, and Allocation

At the analytical price:

```text
pi*=1/3,
dividend_1=(1/4)(1/3)=1/12,
dividend_2=(3/4)(1/3)=1/4,
I_1=5/12,
I_2=7/12.
```

The consumer allocations are

```text
x_1*=(5/8,5/24),
x_2*=(7/8,7/24).
```

The aggregate allocation is `(3/2,1/2)`, exactly equal to aggregate endowment plus net production.

## 7. Candidate Resources and Walras Diagnostics

The formal candidate resource residual uses only the candidate `(x,y)`:

```text
r(x,y)=sum_i x_i-sum_i e_i-sum_j y_j.
```

At the analytical allocation, `r=(0,0)` and the formal candidate Walras residual is `p dot r=0`. Firm and consumer optimality are checked by an independent profit oracle and an independent utility oracle, respectively; market clearing cannot substitute for either check.

## 8. Acceptance Targets

Automated tests and experiments jointly verify:

- feasibility in the firm's production set;
- global maximum profit and `profit_gap`;
- ownership shares adding up to 1;
- aggregate dividends equaling firm profit;
- consumer budgets and utility gaps;
- `consumption - endowment - net production`;
- the second market, which is not used in root finding;
- the formal candidate Walras residual;
- agreement of numerical results with every analytical fraction.
