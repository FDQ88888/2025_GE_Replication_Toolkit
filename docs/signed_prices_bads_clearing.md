# Signed Prices, Bads, and Clearing Rules

## 1. Three Independent Objects

This project strictly separates:

1. `CommodityKind`: semantic GOOD/BAD metadata;
2. `PriceSignRestrictions`: the price-sign region explicitly specified by the economy;
3. `ClearingRule`: commodity-by-commodity exact clearing or free disposal.

`CommodityKind.BAD` does not by itself imply negative utility, a negative price, government regulation, zero consumption, or free disposal.

## 2. Normalization Is Not a Sign Restriction

`normalize_signed_l1(p)` performs only:

```text
p -> p / sum_l |p_l|.
```

It preserves the sign of every coordinate. `rescale_to_fixed_numeraire` permits only positive rescaling; the function explicitly rejects a target numeraire that would require multiplying every price by a negative scalar.

For the benchmark:

```text
fixed-numeraire p=(-1,1),
signed-L1 p=(-1/2,1/2).
```

The round-trip error is zero. The code uses no softmax, `abs(price)`, clipping, or epsilon replacement.

## 3. Consumption Sets Determine Bad Absorption

The default consumption set is `NonnegativeOrthant`. `BoxConsumptionSet` can specify coordinate-wise lower and upper bounds, including:

- upper bounds on bad absorption;
- fixed-zero coordinates in a particular paper example;
- nonnegative, unbounded coordinates for ordinary goods.

These restrictions come from the consumer specification, not from the commodity kind.

## 4. Analytical Negative-Price Bad Benchmark

A consumer has endowment:

```text
e=(b,g)=(1,2).
```

The consumption set and utility are:

```text
0<=b<=1,
g>=0,
u(b,g)=g-(1/2)b.
```

At `p=(-1,1)`, wealth is `p dot e=1`. The budget constraint is:

```text
-b+g<=1,
g<=1+b.
```

Substitution gives the utility bound:

```text
u<=1+b-(1/2)b=1+(1/2)b.
```

Thus the consumer uniquely chooses the maximum absorption level `b=1` and consumes `g=2`. The candidate allocation equals aggregate endowment; both commodities clear exactly, and the utility gap, budget residual, resource residual, and Walras residual are all zero.

This example shows that a negative price can compensate an agent for absorbing a bad. It is not an example from Anderson-Duanmu, nor does it claim that every bad must have a negative price.

## 5. Exact Clearing and Free Disposal

Throughout the project, a residual is defined as demand/allocation minus available resources.

```text
EXACT: residual_l = 0,
FREE_DISPOSAL: residual_l <= 0.
```

A test uses the same candidate residual `(-0.5,0)` to verify that the market check passes when the first commodity is assigned FREE_DISPOSAL and fails when it is assigned EXACT. No generic complementarity condition is added. Any future paper-specific compliance region must be implemented separately from its original definition.
