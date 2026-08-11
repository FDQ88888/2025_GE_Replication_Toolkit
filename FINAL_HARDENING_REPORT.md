# Final Research-Grade Hardening Report

## 1. Executive Summary

本轮是现有 `duanmu_ge_lab` 的加固，不增加经济模型。两个会导致研究语义失真的硬问题已修复：LinearRayTechnology 对理论零利润的浮点误分类，以及 reproducibility suite 对失败实验的假成功。状态、容差、候选量会计、价格尺度、论文参数、依赖、文档、CI 与交付包也完成了系统审计。

最终证据为：CPython 3.12.13 与 3.13.0 均 `113 passed, 0 failed`；16 个 required suite observations 全部精确匹配预期状态；Examples 1-6 为 6/6 `PAPER_REPLICATION_SUCCESS`；两个环境的 strict final audit 均为 `FINAL_AUDIT_PASSED`。

## 2. Original Issues Found

- `p dot v` 的极小正舍入误差会把理论 zero-profit ray 错判为 unbounded profit。
- suite 过去可能只完成调用并打印状态，未强制 actual status 等于 expected status。
- sweep 成功状态未校验发现簇数量；单实验 CLI 对失败状态仍可能返回 0。
- 图表生成没有先拒绝失败的上游结果。
- 环境声明缺少跨 minor 实测、上界与已测试 pins；CI、scope 和机器无关交付说明不足。
- 历史结果元数据记录了解释器与两个配置文件的机器绝对路径。

## 3. LinearRayTechnology Floating-Point Bug

根因是对 `margin = p dot v` 使用精确的 `margin > 0` 分支。修复采用 L2 尺度

```text
scale = ||p||_2 ||v||_2
tol = profit_margin_abs_tol + profit_margin_rel_tol * scale
```

并把 margin 明确分类为 shutdown、numerical zero 或 positive-unbounded。默认值为 `1e-14 + 1e-12*scale`，由统一 tolerance infrastructure 暴露。zero-margin 下任何可行 ray activity 都按非唯一利润最大化解验证，不再和任意返回 plan 比较。

回归测试覆盖 exact zero、`+/-5e-17`、明显 `+/-1e-3`、尺度变化和非唯一活动量。Examples 1-6 与 mapping 重跑后，共同论文数值字段相对修复前快照的最大变化为 0；具体 margin 与分类见 `HARDENING_FIX_01_LINEAR_RAY.md`。

## 4. Reproducibility Suite False-Success Bug

状态现在由集中注册表映射到 SUCCESS/FAILURE/BLOCKED/PARTIAL/SKIPPED/UNKNOWN。每个 YAML runner 明确声明 `expected_status` 和 `required`。suite 保存 expected/actual/outcome，任一 required mismatch、blocked、unknown 或 exception 都产生 `REPRODUCIBILITY_SUITE_FAILED` 和非零退出码；optional skip 只能成为显式 warning。

sweep 只有实际分支计数等于配置目标时才返回 `SWEEP_SUCCESS`；单实验 CLI 只对登记的成功状态返回 0；图表只接受三个精确成功的上游结果。测试覆盖全成功、required failure、required blocked、optional skipped warning、失败退出码、未知单实验状态和失败图表来源。详见 `HARDENING_FIX_02_STATUS_SEMANTICS.md`。

## 5. Cross-Version Testing

Windows 上实际验证 CPython 3.12.13 与 3.13.0，两者均完成 113 tests、compileall 和完整 suite；3.13 另执行 CI 的关键 smoke commands。Ubuntu CPython 3.11/3.12/3.13 GitHub Actions matrix 已配置但尚无远程 run，因此不标记为 verified。精确矩阵见 `TESTED_ENVIRONMENTS.md`。

## 6. Dependency Strategy

`pyproject.toml` 使用 `>=3.11,<3.14`，并为 NumPy、SciPy、PyYAML、Matplotlib、pytest 设置当前已审计 major 上界。`requirements-tested.txt` 是一个真实的 CPython 3.12 reference environment，不声称跨平台 lock。项目未引入未使用的 pandas 或新工具链。

## 7. Documentation Fixes

README 给出 PowerShell、POSIX 和无需 activation 的命令，删除个人路径并立即说明非通用边界。CITATIONS 明确本地查阅的论文 PDF 不进入 clean package。新增 scope、参数来源、研究措辞、环境和协作者文档；教授演示压缩为有限模型研究展示，不使用软件营销式声称。

## 8. Tolerance Audit

`TOLERANCE_AUDIT.md` 逐项记录 market clearing、budget、consumer/firm optimality、profit zero、normalization、clustering、paper comparison 和 policy accounting 的值、尺度与用途。没有通过 rounding、clip 或盲目放宽 tolerance 修复论文结果；solver acceptance 与论文表格舍入容差保持分离。

## 9. Candidate-vs-Reoptimized Audit

资源、市场出清、policy compliance、tax/quota revenue、income 和 Walras accounting 均使用 candidate 自身 allocations/plans。reoptimized quantities 只用于 utility/profit optimality gap。新增 policy-level 回归测试使用内部一致但经济上错误的 cache，确认 diagnostics 仍从 candidate quantity 识别违规。

## 10. Paper Replication Revalidation

Examples 1-6 全部重新运行并返回 `PAPER_REPLICATION_SUCCESS`；Theorems 3-4 mapping 返回 `NUMERICAL_MAPPING_CHECK_SUCCESS`。论文参数均可追溯到正文/Supplement 页码、数学 ledger 和 YAML；搜索区间、起点、scan points 和容差明确标为计算选择。详见 `PAPER_PARAMETER_AUDIT.md`。

## 11. Current Test Result

最终结果：`113 passed, 0 failed`，相对 pre-hardening 的 100 tests 净增 13。新增覆盖 LinearRay margin、非唯一 optimum、状态 contract、sweep validation、candidate policy accounting、价格尺度、CLI exit code 与图表上游门禁。

## 12. Reproducibility Suite Result

CPython 3.12 与 3.13 均为 `REPRODUCIBILITY_SUITE_SUCCESS`。最终 manifest 有 16 个 required observations、0 failures、0 warnings，所有 expected/actual status 精确相等。

## 13. Final Audit Result

Windows CPython 3.12.13 与 3.13.0 均真实返回 `FINAL_AUDIT_PASSED`。审计实际重跑 pytest 与 compileall，并要求 critical results、suite、图、文档、路径、metadata 和 classification 全部满足强制条件；失败会返回非零退出码。

## 14. Known Remaining Limitations

- 非线性 multistart/continuation 不是根的完备认证；发现簇不等于全部均衡。
- Example 4 的非存在来自论文理论，不来自 solver failure。
- paper-specific builders 不是任意 YAML 模型编译器。
- 不支持一般不完全偏好、综合外部性、无限维或测度经济求解。
- finite weighted experiment 是构造相关数值实验，不证明 continuum convergence、uniform integrability 或非标准分析结果。
- CI 尚未远程执行，Python 3.11 仅配置未验证。

## 15. Safe Claims to Professor Duanmu

可以准确称为：围绕 Anderson-Duanmu quota/emission-tax examples 构建的 finite-model paper-replication、equilibrium-search 和 independent numerical-diagnostics framework；Examples 1-6 在当前配置与容差下成功匹配指定目标；多分支结果是已诊断候选的稳定数值发现；结果可在两个本地 Python minor 环境复现。

在标准 diagnostics error/residual 字段中排除允许的 bad-disposal slack 和仅用于尺度判断的 ratio 后，最大关键误差为 `2.148654587585952e-10`，来自 tax sweep 一个已验证 candidate 的 `max_compliance_violation`。

## 16. Claims That Must Not Be Made

不得声称：数值计算证明一般存在性/唯一性；未找到根证明非存在；发现三簇证明恰有三个均衡；有限网格稳定性证明连续极限；项目实现 measure-theoretic/nonstandard analysis；项目是 universal GE solver；未运行的 CI/Python 3.11 已验证。
