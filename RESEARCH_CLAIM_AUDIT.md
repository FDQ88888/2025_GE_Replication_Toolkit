# Research Claim Audit

## 状态语义

源码中的 run-level 状态由 `src/duanmu_ge_lab/experiment_status.py` 集中登记。CLI、reproducibility suite 和 final audit 只接受明确登记且与配置预期完全相同的成功状态；未知、失败、阻塞、部分完成和必需实验的跳过都不能产生成功退出码。

`VERIFIED_CANDIDATE` 只表示给定有限 candidate 在记录的数值容差下通过了当前实现的可行性、预算、最优性、出清、价格和政策会计诊断。它不是存在性、唯一性或搜索完备性证明。

## 逐类检查

| 用词或标签 | 项目中的允许含义 | 明确不允许的推论 |
|---|---|---|
| `PAPER_REPLICATION_SUCCESS` | 配置声明的论文目标、数值比较和必需诊断均通过 | 论文全部一般性定理已经软件证明 |
| `NUMERICAL_MAPPING_CHECK_SUCCESS` | Theorems 3-4 的指定有限实例在两种坐标下数值一致 | 定理本身由程序证明 |
| `DISCOVERED_N_VERIFIED_CANDIDATE_CLUSTERS` | 既定搜索区域、起点和聚类规则发现 `N` 个已诊断簇 | 恰有 `N` 个均衡，或不存在其他根 |
| `NO_VERIFIED_CANDIDATE...` | 搜索或解析预检没有给出可验证 candidate | 一般模型不存在均衡 |
| `NO_EQUILIBRIUM` | 仅在 Example 4 中引用论文的理论结论 | 由 solver failure 推导非存在 |
| solver `success`/`converged` | 数值算法满足自身停止条件 | candidate 自动成为均衡 |
| finite-grid stability | 当前构造下的有限样本数值稳定性 | 测度经济收敛、uniform integrability 或非标准分析结果 |

## 全项目检查结论

- 未发现把 solver 收敛直接改写为均衡存在的 run-level 成功条件；candidate 仍须独立 diagnostics。
- 未发现把零发现或失败起点写成一般非存在证明。
- 多分支输出和图表均使用 `discovered`、`candidate` 与 search-protocol 限定语。
- Example 4 的理论非存在标签与数值预检结果分别保存。
- 图表生成现要求三个上游结果处于精确预期状态，失败结果不能获得 `FIGURE_GENERATION_SUCCESS`。
- finite weighted experiment 明示为 construction-specific numerical experiment，不声称连续极限定理。

因此，教授面前可以陈述的是“有限模型论文复现、候选搜索和独立数值诊断框架”；不应陈述为 universal GE solver、proof assistant、measure-theoretic solver、nonstandard-analysis implementation 或完备均衡枚举器。
