# Duanmu GE Lab - Implementation Plan

> 状态：第一轮历史实施路线，2026-08-09 创建。Milestones 1-11 已于 2026-08-10 实现并通过最终审计；当前完成状态、限制与后续方向以 `REPORT.md`、`FINAL_AUDIT.md` 和 `OPEN_QUESTIONS.md` 为准。本文件保留用于追踪最初设计约束。

## 1. 项目目标与边界

`Duanmu GE Lab` 的目标是建立一个可审计的有限维一般均衡研究工具，用来：

- 复现 Anderson-Duanmu (2025) 的配额与排放税例子；
- 研究生产、坏品、综合外部性、严格市场出清与允许负价格的有限加权经济；
- 搜索并区分多个均衡分支；
- 比较配额产权分配、税收返还、排放水平、价格与福利分配；
- 为将来研究有限经济如何近似测度经济提供实验框架。

不在当前范围内：SAM、GTAP、投入产出表校准、代表性家庭宏观 CGE、动态气候综合评估、深度学习、GPU、Web 前端、数据库、云部署。

## 2. 三层成果结构

### 2.1 Paper Replication

这一层只实现原论文已经定义的经济对象与例子。所有参数、公式和预期结果均引用具体页码、定义、定理或补充材料。

首选复现顺序：

1. **Example 1**：三商品、两代理人、一私人企业的配额经济；有正文给出的唯一解析均衡，可作为符号、预算和市场出清的端到端校验。
2. **Example 2**：改变配额产权在政府企业与私人企业之间的分配，检验价格可能不变而消费和福利分配改变。
3. **Examples 3-4**：同一税率的多个排放税均衡及某些税率无均衡的现象。
4. **Examples 5-6**：同一配额对应多个配额价格，以及配额/税映射的非唯一性。

正文无法支撑的计算细节要等待 Supplementary Material，不做猜测性填补。

### 2.2 General Toolkit

通用层抽象有限消费者、有限企业、生产技术、外部性、政策和诊断。它允许论文例子之外的计算选择，但输出必须标记为 `OUR COMPUTATIONAL CHOICE`。

### 2.3 Future Extensions

- 有限加权消费者；
- 人口离散化与样本规模扫描；
- 参数延拓和均衡分支追踪；
- 与测度经济假设相关的数值诊断，例如坏品吸收上界、经验一致可积性指标；
- 未发表论文中的 quota welfare theorem，待取得原稿后另立里程碑。

这些扩展不进入 MVP，也不改变论文复现层的数学定义。

## 3. 开发门禁

### Gate 0：研究定义冻结

满足以下条件后才能开始核心代码：

- `RESEARCH_NOTES.md` 的论文对象映射经人工确认；
- `OPEN_QUESTIONS.md` 中 `BLOCKING` 项已解决或有明确保守选择；
- 取得 Econometrica Supplementary Material，或明确第一阶段只复现正文信息充分的 Example 1-2；
- 确定第一种价格归一化与税率尺度；
- 确定严格出清/自由处置的逐商品配置方式；
- 确定第一个 MVP 的效用与生产技术表示。

### Gate 1：数学规格测试

每个实现对象先有一页数学规格，至少包括：

- 数学定义；
- 维数与符号约定；
- 输入与输出；
- 假设与不可行状态；
- 来源；
- 可由解析答案验证的最小测试。

### Gate 2：求解器与验证器分离

求解器只能生成 `EquilibriumCandidate`；独立的 `EquilibriumDiagnostics` 决定候选是否达到报告标准。两者不得共享已经缓存的“最优性成立”布尔值。

## 4. 建议的 MVP 数学模型

MVP 是有限、静态、确定性的 Arrow-Debreu 生产经济：

- `I` 个异质消费者，可选人口权重 `lambda_i > 0`，权重和为 1；
- `J` 个企业；
- `L` 种商品，允许 good、bad、regulated 三种相互独立的语义属性；
- 消费集和生产集由显式约束定义；
- 外部性由独立 `ExternalityModel(x,y,p)` 计算；
- 价格允许负、零、正；
- 每种商品分别指定 exact clearing 或 free-disposal inequality；
- 政策为 `NoRegulation`、`QuotaPolicy` 或 `EmissionTaxPolicy`；
- 静态竞争均衡由消费者最优、企业最优、资源/合规条件与价格归一化共同定义。

MVP 不直接尝试表达论文允许的不完备、非传递偏好。首个可计算版本使用连续效用函数代表偏好；这是 **OUR COMPUTATIONAL CHOICE**，接口仍命名为 `PreferenceModel`，避免把“效用函数表示”误当成论文的一般定义。

## 5. 变量、参数与归一化

### 5.1 内生变量

| 变量 | 含义 | 备注 |
|---|---|---|
| `x_i in R_+^L` | 消费者配置 | 必须满足 `X_i` |
| `y_j in R^L` | 企业净生产 | 必须满足 `Y_j` |
| `p in R^L` | 商品价格 | 允许有符号；必须归一化 |
| `s` 或乘子 | 不等式松弛/最优性证书 | 只有采用 KKT/MCP 表述时显式加入 |
| `externality_state` | 排放或综合外部性 | 从候选 `(x,y,p)` 重算，不作为任意自由变量 |

### 5.2 外生政策参数

- 配额：总配额、各企业配额产权、政府企业配额、未监管商品合规区域。
- 排放税：税率向量 `t`、返还向量 `lambda`、合规区域。
- 无监管：逐商品的出清/处置规则。

### 5.3 价格归一化候选

第一选择是论文一致的有符号 `L1` 归一化：

```text
sum_l |p_l| = 1.
```

其数值实现不能简单把绝对值方程交给光滑 root solver。可选实现方式：

1. 固定一个非零坐标为 numeraire，并在诊断中转换回论文的 `L1` 归一化；
2. 枚举价格符号区域，在每个区域内把 `|p_l|` 线性化；
3. 使用带非光滑约束的优化/互补求解；
4. 在已知论文例子的符号模式下固定符号，只用于 paper replication。

MVP 建议：对 Example 1-2 使用论文已知的价格符号模式作复现测试；通用引擎采用“固定非零 numeraire + 显式符号约束”，并保留转换到 `L1` 规范的函数。这样归一化是坐标选择，符号限制仍由经济模型单独给出。

排放税模式还要求 `proj_k(p)=-t`。若同时使用 `L1` 归一化，`t` 是相对价格而不是任意有量纲税额；税率扫描必须记录归一化和单位。

## 6. 均衡条件的数值表达

### 6.1 等式

- 选择了 exact clearing 的商品：资源残差等于 0。
- 配额模式的受监管商品：总净排放精确等于总配额。
- 价格归一化。
- 排放税模式：受监管价格坐标等于 `-t`。
- 政策收入守恒：政府出售配额或征税所得等于返还总额。

### 6.2 不等式

- 消费集、生产集与非负性约束；
- 消费者预算 `p*x_i <= income_i`；
- 允许自由处置的商品，资源残差属于 `R_<=0`；
- 配额/税合规区域中的逐坐标不等式。

预算等式只能在局部非饱和等条件确实保证时作为派生检查，不应无条件强加。

### 6.3 最优性与互补性

有三种实现层级：

1. **解析最优反应**：论文例子和可解析 benchmark 的首选。
2. **嵌套优化 + 市场根求解**：给定价格和外部状态，分别求消费者需求和企业供给，再求市场残差为零。
3. **统一 KKT/MCP**：仅在效用、生产与约束满足适当凸性和可微性时使用；KKT 不是任意非凸问题的充分条件。

第一版不依赖专有 MCP 求解器。优先使用 `scipy.optimize.root`、`least_squares`、`minimize`；`cvxpy` 只用于确实是凸优化的消费者或企业子问题。

## 7. 解析与数值方法分工

### 7.1 必须先解析的内容

- 论文 Example 1 的消费、生产、价格和福利公式；
- 政府/私人配额产权如何进入利润与预算；
- 税收返还总额和 Walras 型会计恒等式；
- 各种归一化之间的变换；
- 简单线性技术下的企业供给边界。

### 7.2 数值方法负责的内容

- 非线性需求和供给；
- 多个市场同时出清；
- 多起点发现多个候选；
- 政策参数扫描和分支延拓；
- 有限人口权重/规模实验。

数值方法不负责证明一般存在性、唯一性或测度经济收敛。

## 8. EquilibriumCandidate 验证协议

一个结果只有同时通过下列独立检查，才能标为 `verified_candidate`：

1. **Domain**：所有变量有限，维数正确，消费和生产属于各自可行集。
2. **Price normalization**：归一化误差低于容差；符号限制独立检查。
3. **Consumer budget**：每个消费者的支出不超过按候选重算的收入。
4. **Consumer optimality**：用独立优化或解析最佳反应重算，报告 utility gap 或 revealed-preference violation。
5. **Firm optimality**：重算最大利润，报告 profit gap。
6. **Market/compliance**：逐商品报告 exact residual、free-disposal slack、配额残差或税合规残差。
7. **Policy accounting**：企业配额收入、政府配额收入、税收、返还及持股分配逐项对账。
8. **Walras law**：报告价值加总残差；它是诊断，不替代逐商品出清。
9. **Complementarity**：只对模型实际包含的互补关系检查乘积残差。
10. **Externality consistency**：从 `(x,y,p)` 重算外部性状态，与偏好计算使用的状态一致。

建议分级：

- `verified_candidate`：全部硬约束和最优性 gap 达到严格容差；
- `approximate_candidate`：可行但一项或多项 gap 只达到宽松容差；
- `solver_point`：求解器返回，但未通过独立验证；
- `failed_run`：无可报告候选，保留原因和初值。

## 9. 多重均衡搜索协议

1. 使用确定性网格、随机种子和理论导出的初值三类起点。
2. 每个起点独立求解并保存求解日志摘要。
3. 只对通过诊断的候选聚类去重。
4. 聚类距离在归一化后的 `(p,x,y)` 上计算，不能只按价格或排放量去重。
5. 记录 basin size，但不把起点命中频率解释为均衡选择概率。
6. 政策扫描优先使用延拓：上一参数点的每条分支作为下一点初值，同时加入独立新起点防止漏分支。
7. 输出“在本搜索协议下发现 N 个候选”，不写“共有 N 个均衡”，除非有解析证明。

## 10. 预期目录结构（第二轮才创建）

```text
duanmu_ge_lab/
  README.md
  pyproject.toml
  src/duanmu_ge_lab/
    core/
      commodity.py
      consumer.py
      firm.py
      economy.py
    preferences/
    technologies/
    externalities/
    policies/
      base.py
      no_regulation.py
      quota.py
      emission_tax.py
    equilibrium/
      system.py
      candidate.py
      diagnostics.py
    solvers/
    experiments/
  configs/
  scripts/run_experiment.py
  tests/
  results/
  docs/
```

这只是计划，不在第一轮创建空骨架，以免目录结构在数学对象尚未冻结时反过来绑架设计。

## 11. 里程碑与验收标准

### Milestone 0 - Research

交付：本轮三份 Markdown。验收：来源、定义、未决问题和开发门禁清楚；无核心代码。

### Milestone 1 - Minimal GE Engine

实现无生产或最小线性生产的有限经济、价格归一化、逐商品出清和诊断。至少一个解析均衡测试。

### Milestone 2 - Production

加入一般 `ProductionTechnology`、利润最大化、企业所有权和股息。验证利润与预算会计。

### Milestone 3 - Weighted Economies

加入消费者人口权重；聚合消费、禀赋和福利均使用同一权重约定。测试“复制消费者不改变总经济”的一致性。

### Milestone 4 - Bads and Exact Clearing

允许负价格、坏品吸收上界、生产副产品和 non-free-disposal。加入 Hara 型压力测试，但只作有限经济实验。

### Milestone 5 - Quota

实现政府企业、企业配额产权、`Z(m)`、配额利润与合规诊断。用 Example 1 解析解验收。

### Milestone 6 - Emission Tax

实现税率固定价格坐标、总排放、政府收入与返还。用 quota-to-tax 会计恒等式做测试。

### Milestone 7 - Paper Replication

复现 Examples 1-2；取得补充材料后复现 Examples 3-6。报告参数、公式、容差、图表与偏差来源。

### Milestone 8 - Multi-equilibrium Search

多起点、去重、分支标识、失败记录；在已知多重均衡例子上验收。

### Milestone 9 - Policy Sweeps

对配额和税率做连续扫描，保存分支、排放、价格和存在候选区域；禁止单线折线掩盖多值关系。

### Milestone 10 - Welfare Distribution

比较配额产权和返还规则对个体效用、加权福利和分配的影响。严格区分 constrained Pareto 与 full Pareto。

### Milestone 11 - Finite Approximation

增加人口规模和权重实验，报告坏品消费尾部、最大个体份额、经验一致可积性指标和均衡残差。结论限于数值证据。

每个里程碑都必须同时交付：自动测试、一个端到端实验、独立诊断摘要、失败实验记录和来源说明。

## 12. 技术栈与编码规范

- Python 3.11+；
- `numpy`, `scipy`, `pandas`, `matplotlib`, `pyyaml`, `pytest`；
- `cvxpy` 仅在凸子问题确有价值时加入；
- `dataclass`、类型标注、短函数、显式输入输出；
- 数学核心 docstring 必须写经济含义、数学定义、参数、返回值和来源；
- 配置采用 YAML，运行接口目标为：

```text
python scripts/run_experiment.py --config configs/example.yaml
```

每次实验保存配置快照、代码版本信息、随机种子、求解器设置、候选与诊断，不伪造参数、不删除失败结果。

## 13. 首次编码轮建议范围

通过 Gate 0 后，第二轮只做 Milestone 1 的最小闭环：

1. 数学对象与数据校验；
2. 有符号价格归一化接口；
3. 一个解析有限 GE benchmark；
4. `EquilibriumCandidate` 和独立 `EquilibriumDiagnostics`；
5. pytest 与简短研究输出。

配额和排放税暂不在同一轮一次性完成。这样每个政策模块都建立在已经验证的资源会计、消费者/企业最优性和价格处理之上。
