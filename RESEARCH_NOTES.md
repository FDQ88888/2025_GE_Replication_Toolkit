# Duanmu GE Lab - Research Notes

> 状态：持续维护的研究设计文档。初版 2026-08-09；2026-08-10 已补入官方 Supplement 来源审计。实现状态以各 Milestone report 为准。

## 0. 研究纪律与证据标签

本项目遵循 `MATHEMATICAL MODEL FIRST. CODE SECOND.`。任何进入代码的数学对象都必须标明来源，并区分以下三类：

- **PAPER DEFINITION**：原论文正文或补充材料中的定义、假设、定理、例子。
- **OUR COMPUTATIONAL CHOICE**：为了有限维计算而额外选择的效用函数、技术集合参数化、归一化坐标、求解器和容差。
- **NUMERICAL APPROXIMATION**：有限网格、多起点、离散人口或残差意义下的近似，不得写成存在性证明。

若一个公式尚未从原始文献核验，必须显式写成 `NOT VERIFIED FROM PRIMARY SOURCE`，并禁止作为论文复现模式的默认实现。

## 1. 已阅读材料与来源状态

### 1.1 用户提供材料

- `Three proofs.pdf`：11 页手写证明，内容为 Slutsky 矩阵、Kakutani-Nash 存在性、第二福利定理。
- `Proof of Microeconomics.pdf`：14 页手写证明，覆盖分离/支撑超平面、Slutsky、vNM 期望效用、Debreu 表示、Berge 最大值、Kakutani、Walras 均衡存在、第一与第二福利定理。
- `Haosui_Duanmu_CV.pdf`：本地 CV，日期为 2025 年 1 月。
- `pasted-text.txt`：项目任务书，明确要求研究级、定义驱动、有限加权 GE、坏品、生产、外部性、配额、排放税和独立诊断。

### 1.2 原始研究文献

1. Robert M. Anderson and Haosui Duanmu, “Cap-and-Trade and Carbon Tax Meet Arrow-Debreu,” *Econometrica* 93(2), 2025, pp. 357-393。已取得并核验官方全文：[Econometric Society PDF](https://www.econometricsociety.org/publications/econometrica/2025/03/01/Cap-and-Trade-and-Carbon-Tax-Meet-ArrowDebreu/file/ecta200778.pdf)。
2. Robert M. Anderson, Haosui Duanmu, M. Ali Khan, and Metin Uyanik, “Existence of Equilibria in Large Competitive Markets with Bads, Production and Comprehensive Externalities,” arXiv:2511.00478v2，2026-05-31 修订。已核验 [arXiv HTML 全文](https://arxiv.org/html/2511.00478v2) 与 PDF。
3. Haosui Duanmu 的本地 CV 与个人研究页。个人旧主页突出数学逻辑、非标准分析、统计与概率；CV 显示其近年的核心研究已经扩展到数学经济学、一般均衡、气候政策、坏品与外部性。[个人主页](https://hyperfinite.net/)

### 1.3 2026-08-10 Supplement 来源审计

2025 Econometrica 论文的 Supplementary Material 已从 Econometric Society 官方地址取得，并保存为：

```text
sources/Anderson_Duanmu_2025_Supplement.pdf
```

文件核验：17 页、423,234 bytes、PDF 1.5，SHA-256 为 `A5013517781FCD37BF38446975DA2F91C033FDEC6709AFF90F702C1652C8524A`。Wiley 正文页将同一附件列为 `ecta200778-sup-0001-onlineappendix.pdf`（Online Appendix, 413.3 KB）。官方正文也已归档为 `sources/Anderson_Duanmu_2025_Econometrica.pdf`。

Supplement 第 3 节明确提供 Examples 1-4 的详细分析：Example 1 为 pp. 11-12，Example 2 为 pp. 12-13，Example 3 为 pp. 13-15，Example 4 为 pp. 15-16。它没有单列 Examples 5-6；但正文 Examples 5-6（期刊 pp. 382-384）分别完全建立在 Examples 3-4 的经济和均衡分支上。因此，结合正文与 Supplement，Examples 3-6 的 primary-source gate 已解除。编码前仍须为每个例子建立逐参数、逐公式 ledger，不能只照抄图表数值。

“The Second Welfare Theorem for Quota Equilibrium”及 CV 所列其他在写论文仍只有书目信息或独立 working-paper 状态；未完整核验前不把其定义写入核心实现。

## 2. 端木昊随老师研究方向与本项目定位

从 CV 和已发表论文看，与本项目最相关的研究主线是：

- 数学经济学与一般均衡存在性；
- 生产经济、坏品、非自由处置和允许负价格；
- 消费与生产引起的综合外部性；
- cap-and-trade、quota equilibrium、carbon/emission tax equilibrium；
- 配额产权分配、税收返还与福利分配；
- 有限加权经济到测度经济的推广；
- 非标准分析、超有限经济与 Loeb 测度方法。

CV 中直接相关的已发表工作包括：

- Anderson and Duanmu (2025), *Econometrica*：配额与排放税进入 Arrow-Debreu 生产经济。
- Anderson, Duanmu, Khan, and Uyanik (2022), *Economic Theory*：含/不含自由处置的无限代理人 Walras 均衡。
- Anderson and Duanmu (2025), *Games and Economic Behavior*：均衡与社会规范。
- Anderson, Duanmu, Khan, and Uyanik (2022), *Journal of Mathematical Economics*：局部凸拓扑向量空间中的抽象经济。

因此，`Duanmu GE Lab` 的正确学术定位是：**对端木老师相关一般均衡模型做可审计的有限维计算研究，并为以后研究坏品、外部性、政策与大经济近似提供工具**。它不是基于 SAM/GTAP 的宏观校准 CGE，也不是用一个 Cobb-Douglas 代表性家庭展示“碳税效果”的普通程序。

## 3. Anderson-Duanmu (2025) 的有限配额经济

以下均为 **PAPER DEFINITION**，来源主要为正文 Definition 3.1-3.5，pp. 363-366。

### 3.1 基本对象

- 有限代理人集合：`Omega`。
- 有限生产者集合：`J`；配额经济中包含政府企业 `j=0`，且 `Y_0={0}`。
- `l` 种商品；前 `k` 种由政府监管。
- 消费集 `X_omega subset R_+^l` 非空、闭、凸。
- 生产集 `Y_j subset R^l` 非空，生产向量以净产出记号表示。
- 配置空间 `A = product_omega X_omega`。
- 全球偏好可依赖其他人的消费、全部企业生产及价格；代理人给定这些外部状态，只选择自己的消费。
- `theta_omega_j >= 0` 是代理人对企业的持股比例，且对每个企业 `sum_omega theta_omega_j = 1`。
- `e_omega in R_+^l` 是初始禀赋。

### 3.2 有符号价格与归一化

论文的价格集合为

```text
Delta = {p in R^l : ||p||_1 = sum_n |p_n| = 1}.
```

论文明确允许负价格，负价格可解释为坏品或排放的价格。配额价格定义为受监管商品价格的相反数：`q = -proj_k(p)`。

这给出两个不可混淆的概念：

- **价格归一化**：消除齐次性，例如 `||p||_1=1` 或选择 numeraire。
- **价格符号限制**：是否允许某些坐标为负、零或正。

代码不得使用 softmax 强制所有价格为正。

### 3.3 配额产权与合规区域

政府给企业 `j` 分配受监管商品的配额。论文用

```text
m^(j) in R_<=0^k
```

表示企业配额的负数，并令 `m = sum_j m^(j)`。`-m^(j)` 是企业 `j` 的排放产权，`-m` 是总配额。

配额合规区域为

```text
Z(m) = {m} x product_{k<n<=l} Z(m)_n,
```

其中每个未监管商品坐标 `Z(m)_n` 可以是 `{0}`（严格市场出清）或 `R_<=0`（允许自由处置）。因此，“是否自由处置”必须逐商品配置，不能作为一个隐藏的全局默认值。

两个极端制度：

- **cap-and-trade**：配额产权全部给私人企业。
- **global quota equilibrium**：配额产权全部给政府企业，由政府企业持股比例决定收入返还。

### 3.4 预算、利润与需求

代理人的配额预算集为

```text
B^m_omega(y,p) = {
  z in X_omega :
  p*z <= p*e_omega
         + sum_j theta_omega_j [p*y_j + proj_k(p)*m^(j)]
}.
```

企业 `j` 的利润为

```text
pi_j^m(p,y_j) = p*y_j + proj_k(p)*m^(j).
```

配额产权项对 `y_j` 是常数，所以企业供给仍满足

```text
S_j^m(p) = argmax_{z in Y_j} p*z.
```

但是配额总量和产权分配会通过均衡价格、企业利润和家庭收入间接改变生产、消费与福利。政府企业的利润完全来自出售其配额，并按政府设定的政府企业持股比例返还给代理人。

### 3.5 配额均衡

`(x_bar, y_bar, p_bar)` 是 `Z(m)`-compliant quota equilibrium，当且仅当：

1. 每个代理人的 `x_bar_omega` 属于给定外部状态和价格下的需求集；
2. 每个企业 `y_bar_j` 在价格 `p_bar` 下利润最大化；
3. 总资源残差满足

```text
sum_omega x_bar_omega
- sum_omega e_omega
- sum_j y_bar_j in Z(m).
```

对受监管坐标，这意味着总净排放精确等于预设总配额；对未监管坐标，是精确出清还是允许剩余取决于 `Z(m)_n`。

### 3.6 已核验的定理与例子

| 结论 | 论文中的逻辑地位 | 实现含义 |
|---|---|---|
| 对每个满足假设的可行配额，配额均衡存在 | **Theorem 1**, pp. 370-371 | 数值失败不能解释为“不存在”；先查假设、参数化和求解器 |
| 仅由总净排放产生外部性且未监管商品非自由处置时，配额均衡是给定同一排放水平下的约束弱 Pareto 最优 | **Theorem 2**, pp. 373-374 | 福利诊断必须固定总排放后比较；不能直接宣称全局 Pareto 最优 |
| 配额产权分配影响消费和个体福利 | **Example 2** | `quota rights`、企业持股与返还规则必须是一等数据 |
| 每个配额均衡可在相应税率和返还规则下实现为排放税均衡 | **Theorem 3**, p. 376 | 转换依赖价格和返还；不是同一个政策对象自动等价 |
| 每个排放税均衡可实现为 global quota equilibrium | **Theorem 4**, p. 377 | 对应总配额由该税均衡的内生排放确定 |
| 某些税率没有排放税均衡 | **Examples 3-4**，不是一般不存定理 | 税率扫描必须记录无候选区，但不得把求解失败直接标成不存 |
| 同一税率可对应不同排放量 | **Examples 3-4** 的多重均衡现象 | 必须多起点和分支追踪，不能只保留一个根 |
| 同一配额可对应不同配额价格 | **Examples 3-6** 的多重均衡现象 | 配额实现目标量，但价格可能不唯一 |

Supplement 取得后的复现状态：

| 例子 | Primary-source 状态 | 依赖 |
|---|---|---|
| Example 1 | `SOURCE_READY` | 先完成 production 与 quota 会计 |
| Example 2 | `SOURCE_READY` | Example 1 架构、第二企业与产权分配 |
| Example 3 | `SOURCE_READY` | emission-tax 会计、非线性需求、多根搜索 |
| Example 4 | `SOURCE_READY` | 线性技术、边界供给对应、连续均衡集合 |
| Example 5 | `SOURCE_READY` | Example 3 的全部分支与 quota/tax 映射 |
| Example 6 | `SOURCE_READY` | Example 4 的全部分支与 quota/tax 映射 |

## 4. Anderson-Duanmu (2025) 的排放税经济

以下为 **PAPER DEFINITION**，来源为 Definition 4.1、Remark 4.2、Definition 4.3，pp. 375-376。

### 4.1 政策对象

- 所有企业均为私人企业；税模型没有配额模型中的政府企业。
- `lambda_omega >= 0` 是政府返还份额，`sum_omega lambda_omega = 1`。
- 前 `k` 个受监管商品的合规区域坐标为 `R_<=0`，允许任意净排放，但征收排放税。
- `t` 是前 `k` 个商品的排放税率向量。

总净排放定义为

```text
C(x,y) = proj_k(
  sum_omega e_omega + sum_j y_j - sum_omega x_omega
).
```

政府税收为 `t*C(x,y)`，并按 `lambda` 返还。

### 4.2 税收预算与均衡

代理人的预算集为

```text
B^t_omega(x,y,p) = {
  z in X_omega :
  p*z <= p*e_omega
         + sum_j theta_omega_j p*y_j
         + lambda_omega t*C(x,y)
}.
```

`(x_bar,y_bar,p_bar)` 是排放税均衡，当且仅当：

1. `proj_k(p_bar) = -t`，即税率固定受监管商品的负价格；
2. 每个消费者在含返还收入的预算集中最优；
3. 每个企业最大化 `p_bar*y_j`；
4. 总资源残差属于税模型的合规区域 `V`。

税率和返还方案由政府事先给定；总净排放由均衡内生决定。这里存在一个重要的数值尺度问题：论文同时使用 `||p||_1=1` 和 `proj_k(p)=-t`。因此税率是归一化价格体系中的相对价格，代码中的税率扫描必须与归一化方案共同解释。

## 5. 大经济、坏品与综合外部性

本节依据 arXiv:2511.00478v2 的 **PAPER DEFINITION**。

### 5.1 测度生产经济

Definition 4.2 以概率空间 `(Omega,B,mu)` 表示消费者总体，企业集合仍有限。关键对象包括：

- 可积配置 `x in L1(Omega,R_+^l)`；
- 生产向量 `y in product_j Y_j`；
- 有符号归一化价格 `p in Delta`，其中 `||p||_1=1`；
- 全局偏好可依赖整个消费配置、全部企业生产、价格及自身消费；
- 持股密度 `theta_omega_j` 满足 `integral theta_omega_j dmu = 1`；
- 禀赋密度 `e in L1`。

预算、企业利润最大化与有限经济具有同样的 Arrow-Debreu 结构。非自由处置均衡要求精确市场出清：

```text
integral x dmu - integral e dmu - sum_j y_j = 0.
```

### 5.2 坏品不是简单的枚举标签

论文把前 `k` 个商品作为用于技术假设的“坏品类别”，其消费集投影具有可积上界；后续商品为允许无界消费的“商品”。但论文明确指出，个体不必一致认为某个对象是坏品，同一对象可以是 mixed manna。

因此代码中的 `CommodityKind.GOOD/BAD` 只用于语义、配置校验和默认诊断，不得自动推出：

- 所有人对它单调递增或递减；
- 它的价格必然为正或负；
- 它可以自由处置；
- 它必然受到政策监管。

### 5.3 非自由处置与负价格

论文的经济逻辑是：生产副产品不能在会计上消失；若坏品处置会产生外部性，就必须允许负价格提供吸收、消除或封存的激励。强单调性和生产自由处置会排除所需的负价格，因此不能作为默认假设。

消费者对坏品的吸收能力需要可积上界。这个假设用于避免 Hara (2005) 例子中有限经济均衡配置缺乏一致可积性、极小人群吸收几乎全部坏品的问题。

### 5.4 有限加权与测度经济定理

- **Theorem 1**：在有限加权生产经济、凸偏好、可行性/生存与生产集合条件下，均衡存在。
- **Theorem 2**：在 Polish 消费者空间、坏品消费可积有界、偏好弱拓扑连续等条件下，测度生产经济存在均衡。
- **Supplementary Theorem 3**：把正排放上限加入测度配额经济，给出配额均衡存在性。

论文的证明路线是：有限加权定理 -> 超有限提升 -> transfer principle -> Loeb 经济均衡 -> 在更强连续性下压回原测度经济。

### 5.5 本项目能做和不能宣称的事情

Python 可以实现有限加权经济，并把一组权重 `lambda_i` 解释为原子概率质量。增加有限代理人数量可以研究数值稳定性、经验分布和近似行为。

但是：

- 有限离散化不是 Loeb 测度构造；
- 多个有限样本上的稳定结果不是测度经济存在性证明；
- 数值收敛图不是一致可积性、弱紧性或可测选择证明；
- 本项目第一阶段不实现超实数、hyperfinite 对象或 transfer principle。

## 6. 你的证明基础与项目的连接

### 6.1 `Three proofs.pdf`

- **Slutsky 矩阵**：已形成从支出函数、Shephard 引理到对称性和半负定性的链条。它适合支撑个体需求模块的解析 benchmark、比较静态与导数检查。进入正式理论文档前，还要把可微性、内部解、唯一性和局部/全局最优条件写齐。
- **Kakutani-Nash**：最佳反应对应的非空、凸值、闭图/上半连续与紧凸定义域构成完整骨架。这与一般均衡存在性的对应方法直接相关，但代码只能验证某个有限实例的残差，不能“计算出 Kakutani 定理”。
- **第二福利定理**：凸分离、支撑价格和财富转移的主线正确，是理解配额产权、政府返还与支持价格的最佳入口。需要特别保留 LNS、凸性、可行集几何、价格非零及准均衡到均衡的条件。

### 6.2 `Proof of Microeconomics.pdf`

这份笔记已经覆盖本项目所需的理论工具链：支撑/分离、最大值定理、固定点、Walras 均衡存在与福利定理。当前主要问题不是“证明数量少”，而是一些证明把定理假设、对应的连续性概念和边界情形压缩得太快。

建议以后把每个证明改成五栏式研究笔记：

1. 精确定理陈述；
2. 假设清单及每条假设的使用位置；
3. 证明主引理；
4. 容易失效的边界或反例；
5. 对计算模型的含义。

## 7. Mathematical Object -> Code Object Map

| 数学对象 | 计划中的代码对象 | 首轮语义约束 |
|---|---|---|
| 消费者/代理人 | `Consumer` | id、人口权重、禀赋、持股、配额产权/政府返还、偏好、外部性暴露 |
| 企业 | `Firm` | 生产技术、持股、投入/产出、坏品副产品、政策会计 |
| 商品 | `Commodity` | 名称、索引、语义 kind、是否监管、出清制度；kind 不自动决定符号或处置 |
| 禀赋向量 | `EndowmentVector` 或数组字段 | 维数与商品顺序强校验 |
| 偏好 | `PreferenceModel` / `UtilityModel` | 论文允许不完备偏好；可计算 MVP 需明确选择可数值优化的表示 |
| 生产集合 | `ProductionTechnology` | 用约束/可行集表示，不把排放副产品从会计中删除 |
| 外部性 | `ExternalityModel` | 独立于效用形式；由 `(x,y,p)` 计算状态或偏好参数 |
| 经济 | `Economy` | 聚合消费者、企业、商品、权重、产权与出清规则 |
| 政策 | `PolicyBase` | 统一生成预算调整、企业收入、政策约束与会计诊断 |
| 无监管 | `NoRegulation` | 不暗含所有商品自由处置 |
| 配额 | `QuotaPolicy` | 总配额、企业配额、政府配额、合规区域、配额价格 |
| 排放税 | `EmissionTaxPolicy` | 税率向量、返还向量、税收与受监管价格限制 |
| 均衡方程 | `EquilibriumSystem` | 变量编码、约束、残差；与求解器解耦 |
| 候选解 | `EquilibriumCandidate` | 原始变量、状态、来源起点、求解状态、残差 |
| 验证器 | `EquilibriumDiagnostics` | 独立重算最优性、出清、预算、政策会计、归一化与互补条件 |

## 8. 必须冻结的设计不变量

1. 论文定义、计算选择和数值近似必须在文档、配置和输出中分别标注。
2. 价格归一化与价格符号限制是两个独立模块。
3. 不默认自由处置；每种商品的出清条件显式配置。
4. 政策收入只在一个政策会计层计算，消费者预算和诊断共享同一数学来源。
5. 求解器返回 success 不是均衡；均衡候选必须通过独立诊断。
6. 求解失败不是不存在证明；“无均衡”只能引用论文定理/例子，或写成“在给定搜索协议下未发现候选”。
7. 多重均衡研究保留所有通过聚类去重后的候选、失败起点和分支信息。
8. 有限人口实验只称为有限加权计算或有限近似，不声称实现了测度经济和非标准分析证明。

## 9. 第一轮结论

最稳妥的主线不是直接编写一个“大而全”的碳税模拟器，而是先建立一个允许有符号价格、生产、外部性和逐商品出清规则的有限 GE 核心；在其上分别实现论文的 `QuotaPolicy` 与 `EmissionTaxPolicy`，并以正文 Examples 1-2 的解析结果和 Examples 3-6 的多重均衡现象作为复现目标。

后续核心代码必须继续遵守 `OPEN_QUESTIONS.md` 中各模块的 `BLOCKING` 门禁。Supplement 缺失问题已解决；当前重点转为生产会计、逐例参数 ledger、配额/税率归一化和独立最优性诊断。

## 10. Milestone 5 配额复现结论

Definitions 3.2-3.5 的有限配额会计已经实现并通过 Examples 1-2：

- emissions 保持为原商品坐标，没有增加 permit commodity；
- `m^(j)<=0` 是企业排放产权的带符号表示，`m=sum_j m^(j)`；
- 企业总利润为 `p dot y_j + proj_k(p) dot m^(j)`；
- 政府企业 `Y_0={0}`，收入通过政府企业持股分配；
- 消费者预算与 diagnostics 共用 `QuotaEconomy.income_breakdowns`；
- 正式政策 Walras 检查为 `p dot r - proj_k(p) dot m=0`；
- Example 2 在总配额、价格、技术和聚合消费不变时，仅改变产权就改变个体收入与消费分布。

Example 2 原文没有给出基数效用函数，因此项目只复现逐代理人电力消费和同一排放水平下的福利序，不生成虚构的“论文效用值”。完整证据见 `MILESTONE_5_QUOTA_REPORT.md`。

## 11. Milestone 6 税收会计与映射结论

排放税中的 `t` 与 signed-L1 价格共享尺度，必须满足 `proj_k(p)=-t`。因此 numeraire 转换必须同时缩放 `p` 与 `t`；只转换其中一个会改变经济问题。

税收预算使用候选配置产生的 `C(x,y)` 与 `t dot C(x,y)`。Example 1 的全球配额候选通过 Theorem 3 公式映射为税收候选，再按 Theorem 4 映回全球配额候选，两端均通过独立诊断。这个结果是理论映射的数值核对，不替代论文证明。

## 12. Examples 3-6 的多重均衡证据

Example 3 说明同一税率对应多组价格比和排放；Example 5 进一步表明，为某一分支选择能达到 30% 减排的税率，另外两条分支仍会产生不同减排。Example 4/6 的线性技术则在 `t=1/4` 产生排放连续体。相反，配额把受监管资源差直接固定为 `m`，但 Example 5 的同一配额出现三个不同配额价格。

这些结果支持后续把 correspondence 而不是单值函数作为图和数据结构。数值程序保留每个验证分支，不取平均，也不只保留第一个根。
