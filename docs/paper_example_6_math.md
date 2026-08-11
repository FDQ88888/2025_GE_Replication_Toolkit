# Paper Example 6: Mathematical Ledger

## Sources and relation to Example 4

Main article PDF page 28 (journal page 384), Example 6. The construction reuses
Example 4 and its Supplement Section 3.4 derivation.

Choose a desired emissions level `v_hat<1`. Example 4 shows:

- `t<1/4` produces emissions one;
- `t=1/4` permits every emissions level in `[0,1]`;
- `t>1/4` has no equilibrium.

Therefore no tax rate guarantees `v_hat<1`.

The corresponding quota economy adds a government firm with `Y_0={0}`, assigns all
quota rights `m=-v_hat` to it, and gives the sole agent all firm ownership. The
compliance region is `{m}x{0}^2`. Every verified quota candidate must have emissions
exactly `v_hat`.

The checked instance is `v_hat=1/2`. Mapping the Example 4 `t=1/4` branch gives

```text
p=(-1/4,1/4,1/2),
x=(0,0,3/4),
y_1=(1,-1,1),
y_2=(-1/2,0,-1/4),
m=-1/2.
```

The result is an explicit numerical check of the paper construction, not a proof
that every quota equilibrium has the target; that universal statement is sourced to
the paper definition and theorem.
