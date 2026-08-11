# FINAL AUDIT AFTER HARDENING

## 当前门禁状态

**`FINAL_AUDIT_PASSED`。** 加固后代码已在 Windows CPython 3.12.13 与 3.13.0 上分别完成 `113 passed, 0 failed`、compileall、完整 reproducibility suite 和 strict final audit；Examples 1-6 均成功，16 个 required suite observations 精确匹配。

## 环境分层

- Original development environment：pre-hardening CPython 3.12.13，100 tests，旧 audit 与旧 suite 通过；证据保存在 `hardening/pre_hardening/`。
- Current verified environments：Windows CPython 3.12.13 与 3.13.0；精确依赖和执行范围见 `TESTED_ENVIRONMENTS.md`。
- CI environments：Ubuntu CPython 3.11、3.12、3.13 matrix 已配置。当前状态仅为 **CI CONFIGURED**，不是 CI verified。

## 加固后新增强制检查

最终审计现在实际运行 pytest 与 compileall，要求 baseline、全部 critical paper results、suite manifest 和六张研究图精确通过；同时检查 config/reproducibility metadata、异常 candidate classification、个人绝对路径、Markdown 本地链接、必需文档、package metadata 与 README 中的过期硬编码测试数。任何 required failure 都返回非零退出码。

---

# Historical Final Audit Before Hardening

以下内容完整保留上一轮审计历史；其中的 `100 passed` 只描述 pre-hardening 状态，不是当前 README 声称。

## 审计结论

**FINAL_AUDIT_PASSED。** 自动制品审计覆盖 15 份里程碑结果和 6 张研究图，累计读取 130 个 `VERIFIED_CANDIDATE` 分类，未发现其他 candidate classification。最终测试门禁为 `100 passed`，`python -m compileall -q src scripts paper_replications` 通过。

这个结论表示：当前有限模型、保存结果、图表和复现信息在既定测试与容差下内部一致。它不表示已经证明一般均衡存在、唯一、分支完备或有限经济收敛到测度经济。

## 1. Paper Fidelity

**通过，范围受限。**

- 正文和 Supplement 均来自 Econometric Society 官方来源；页码与例子映射记录在 `CITATIONS.md`。
- Quota 使用排放商品坐标和论文产权会计，没有增加 permit commodity。
- Tax 保持 `proj_k(p)=-t`，价格与税率在规范转换时共同缩放。
- Examples 1-6 均先有数学 ledger、来源位置和配置，再有代码。
- Theorems 3-4 只称数值核对；Example 4 的 `NO_EQUILIBRIUM` 只归于论文理论。

剩余边界：代码没有覆盖论文最一般的偏好关系、无限维经济或全部存在性假设。

## 2. Mathematical Correctness

**通过当前实现对象的解析与回归门禁。**

- candidate clearing 使用 candidate allocations/production；reoptimized demand 只验证最优性。
- Walras residual 使用 candidate resource residual。
- 消费者和企业均有显式可行性、预算/利润和最优性 gap。
- `consumption - endowment - net production` 的符号在各层一致。
- normalization、sign restriction、clearing rule、commodity semantics 分离。
- population weights 不作为 welfare weights。
- quota/tax budget 与 diagnostics 调用同一政策会计层。

解析交换、生产、负价坏品、Examples 1-2 和论文表格构成相互独立的校验点。

## 3. Numerical Robustness

**通过既定搜索协议；不作完备性承诺。**

- 标量解析结构优先使用 Brent；目标方程使用 SciPy root/least-squares。
- 多起点包含 deterministic、random 和 continuation，并保存显式 seed。
- 只有完整诊断通过的 candidate 才进入聚类。
- 聚类距离不只比较价格，也比较配置、生产和政策量。
- 税率扫描同时使用 continuation 与 fresh multistart，并保留失败计数。
- 论文理论非存在与 numerical search status 分开。

残余风险：非线性系统仍可能漏根；聚类阈值和有限网格不能替代区间认证或解析证明。

## 4. Software Reproducibility

**通过。**

- 所有 YAML 声明可导入的 runner；统一入口为 `scripts/run_experiment.py`。
- `scripts/run_reproducibility_suite.py` 按依赖顺序重建全部结果和图。
- 每份里程碑 JSON 含 `config_snapshot` 与 `reproducibility`。
- 元数据包括 UTC 时间、Python、依赖版本、Git commit（不可用时明确为 null）、seed 与数值设置位置、候选状态汇总。
- 六张 PNG 有轴、图例、标题、caption、源 JSON 和 SHA-256 manifest。
- `.venv`、cache、egg-info、build 和 coverage 已由 `.gitignore` 排除。

当前目录不属于 Git work tree，因此结果诚实记录 `git_commit: null`；这不是伪造版本号。

## 5. Research Integrity

**通过。**

- paper replication、numerical mapping check、software benchmark 和 paper-inspired experiment 使用不同标签。
- 没有把 solver success 当均衡，也没有把 solver failure 当非存在证明。
- 没有把发现三个候选簇写成“恰有三个均衡”。
- 没有为 Example 2 虚构基数社会福利。
- 没有把尾部统计写成一致可积性证明，也没有声称实现 Loeb measure 或 hyperfinite economy。
- 失败运行和非验证计数被保留在参数扫描结果中。

## 6. Final Evidence

```text
pytest:                     100 passed
compileall:                 passed
persisted milestone files: 15
research PNG figures:       6
recorded verified classes:  130
artifact audit:             FINAL_AUDIT_PASSED
```

机器可读证据位于 `results/final_audit.json`；图表清单位于 `figures/figure_manifest.json`。

## 7. Remaining Risks

1. Examples 3-6 的计算表示忠于已核验有限例子，但不是论文一般理论的完整软件化。
2. 分支发现依赖搜索区间、起点和容差；尚无完备根认证。
3. YAML 能修改已暴露参数，但并非任意偏好或技术都可仅靠配置添加。
4. 当前福利结论限于固定排放的逐代理人比较。
5. 有限加权实验尚未连接到一个已证明的测度经济收敛定理。

这些限制已同步写入 README、REPORT 与 OPEN_QUESTIONS，不阻止当前有限研究工具作为下一阶段工作的可靠基线。
