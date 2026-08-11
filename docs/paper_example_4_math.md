# Paper Example 4: Mathematical Ledger

## Sources and primitives

Main article PDF pages 24-26 (journal pages 380-382), Example 4 and Claims 5.1-5.3;
Supplement PDF pages 15-17, Section 3.4.

There is one agent with `X={0}xR_+^2`, `e=(0,1,0)`, and demand only for
electricity. Two private production rays are

```text
Y_1={(r,-r,r):r>=0},
Y_2={(-2s,0,-s):s>=0}.
```

The agent owns both firms and receives all tax revenue. Compliance is
`V=R_- x {0}^2`.

## Claims

An emission-tax equilibrium exists if and only if `t<=1/4`.

For `0<=t<1/4`, every equilibrium has emissions one, with the candidate

```text
p=(-t,1/2-t,1/2),
x=(0,0,1),
y_1=(1,-1,1),
y_2=(0,0,0).
```

At `t=1/4`, every `v in [0,1]` is supported by

```text
p=(-1/4,1/4,1/2),
x=(0,0,(1+v)/2),
y_1=(1,-1,1),
y_2=(v-1,0,(v-1)/2).
```

For `t>1/4`, the paper status is `NO_EQUILIBRIUM`. The numerical report keeps this
paper theorem separate from its own search/feasibility status.
