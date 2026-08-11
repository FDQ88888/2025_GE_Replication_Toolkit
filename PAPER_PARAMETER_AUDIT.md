# Paper Parameter Audit

## 审计结论

Examples 1-6 与 Theorems 3-4 数值映射所用的论文参数均可追溯到项目中的数学 ledger、YAML 配置和 `CITATIONS.md` 所列官方来源。未发现只存在于 solver 内、却被冒充为论文定义的神秘常数。论文参数与计算参数保持分离：前者定义被复现的经济，后者只控制搜索、求根、去重和数值比较。

## 来源映射

| 对象 | 论文来源 | 进入计算的论文量 | 对应配置与数学说明 |
|---|---|---|---|
| Example 1 | 正文 PDF 11-12 页、期刊 367-368 页；Supplement 11-12 页，Claims 3.1-3.2 | 商品、偏好、技术、产权会计及演示实例 `v=0.5` | `configs/paper/example_1.yaml`；`docs/paper_example_1_math.md` |
| Example 2 | 正文 PDF 12-13 页、期刊 368-369 页；Supplement 12-14 页，Claims 3.3-3.4 | 三消费者、两种 quota-rights regimes 及演示实例 `v=3` | `configs/paper/example_2.yaml`；`docs/paper_example_2_math.md` |
| Example 3 | 正文 PDF 21-24 页、期刊 377-380 页，Table I；Supplement 13-15 页 | 需求公式、价格坐标、Table I 的 `tau=0.010` 与舍入目标 | `configs/paper/example_3.yaml`；`docs/paper_example_3_math.md` |
| Example 4 | 正文 PDF 24-26 页、期刊 380-382 页，Claims 5.1-5.3；Supplement 15-17 页 | 边界税率 `0.25`、边界上下实例和论文理论非存在标签 | `configs/paper/example_4.yaml`；`docs/paper_example_4_math.md` |
| Example 5 | 正文 PDF 26-28 页、期刊 382-384 页，Tables II-III；继承 Example 3 | 30% reduction target、表中税率/减排率和 quota-price 目标 | `configs/paper/example_5.yaml`；`docs/paper_example_5_math.md` |
| Example 6 | 正文 PDF 28 页、期刊 384 页；继承 Example 4 | `v_hat=0.5` 与 supporting tax rate `0.25` | `configs/paper/example_6.yaml`；`docs/paper_example_6_math.md` |
| Theorems 3-4 mapping | 正文 PDF 20-21 页、期刊 376-377 页 | quota/tax 映射及 signed-L1 与 numeraire 坐标关系 | `configs/paper/theorem_3_4_mapping.yaml`；Examples 1 与 policy 文档 |

这里的 `v=0.5`、`v=3`、边界两侧采样点和边界排放网格，是在论文允许的参数族中选取的可复现实例；数学 ledger 已将“论文一般公式”和“本项目检查实例”分开。它们不是为修复测试而调整的数值。

## 计算选择

以下量不是论文的经济原始参数：

- initial guesses、multistart seeds、continuation starts；
- root brackets、scan bounds、scan point counts、maximum evaluations；
- solver residual acceptance、root/cluster deduplication tolerances；
- paper table rounding comparison tolerances；
- 用于展示边界连续集的有限采样网格。

这些量保存在 YAML 的 `solver`、`comparison` 或明确命名的计算字段中。其数值含义和风险见 `TOLERANCE_AUDIT.md`。改变这些量可能改变“在既定搜索协议下发现了什么”，但不得改变论文模型本身，也不得被解释为解析存在性或完备性结论。

## 未解决来源问题

本轮没有发现影响 Examples 1-6 当前复现状态的未知参数来源。尚未取得或确认的其他 working papers 仍列在 `OPEN_QUESTIONS.md`，未被本项目当作已核验定理实现。
