# Delivery Manifest

## 教授建议先看

1. `PROFESSOR_DEMO.md`：3-5 分钟研究定位、论文关系、结果与边界。
2. `README.md`：可运行命令、实现范围、claim boundaries 与导航。
3. `FINAL_HARDENING_REPORT.md`：硬漏洞、测试证据、双环境验证、最大关键残差与仍不可声称的内容。

## 推荐完整阅读顺序

1. `PROFESSOR_DEMO.md`
2. `README.md`
3. `docs/paper_example_3_math.md` 与 `MILESTONE_7_EXAMPLES_3_6_REPORT.md`
4. `figures/tax_emission_correspondence.png` 与 `results/milestone9_tax_quota_sweeps.json`
5. `FINAL_HARDENING_REPORT.md`、`FINAL_AUDIT.md` 与 `TESTED_ENVIRONMENTS.md`
6. `src/`、`paper_replications/`、`scripts/` 与 `tests/`

## 主要文件

| 路径 | 用途 |
|---|---|
| `README.md` | 项目定位、安装、smoke commands、配置边界和结果导航 |
| `PROFESSOR_DEMO.md` | 面向理论研究者的简短展示材料 |
| `REPORT.md` | 项目整体研究报告 |
| `FINAL_HARDENING_REPORT.md` | 最终加固过程与定量证据 |
| `FINAL_AUDIT.md` | 加固后审计及保留的历史审计 |
| `PRE_HARDENING_AUDIT.md` | 加固前真实基线摘要 |
| `HARDENING_FIX_01_LINEAR_RAY.md` | zero-margin 浮点漏洞及重验证 |
| `HARDENING_FIX_02_STATUS_SEMANTICS.md` | false-success 漏洞及状态契约 |
| `TOLERANCE_AUDIT.md` | 关键数值容差的逐项语义 |
| `PAPER_PARAMETER_AUDIT.md` | Examples 1-6 参数来源与计算选择 |
| `RESEARCH_CLAIM_AUDIT.md` | SUCCESS/VERIFIED/EXISTENCE 等措辞边界 |
| `TESTED_ENVIRONMENTS.md` | 两个真实本地环境与未运行 CI 的区分 |
| `CITATIONS.md` | 书目信息、官方链接与 source-page 映射 |
| `OPEN_QUESTIONS.md` | 尚未解决的理论和研究方向 |
| `COLLABORATOR_GUIDE.md` | 新有限模型接入所需数学信息 |
| `docs/SCOPE_AND_LIMITATIONS.md` | 通用性与未实现能力的精确边界 |
| `requirements-tested.txt` | CPython 3.12 已验证参考环境 pins |
| `.github/workflows/tests.yml` | CPython 3.11/3.12/3.13 CI 配置 |
| `results/reproducibility_suite.json` | 16 个 required observations 的机器可读状态 |
| `results/final_audit.json` | strict final audit 的机器可读证据 |

论文 Examples 1-6 的数学 ledger 位于 `docs/paper_example_1_math.md` 至 `docs/paper_example_6_math.md`；每一阶段的历史报告、研究笔记和实现计划均保留。

## Clean Archive

教授版文件名为 `duanmu_ge_lab_hardened_source.zip`。它保留源码、测试、配置、文档、必要结果和图表，但明确排除：

- `.venv/`、`.venv313/` 与其他本地虚拟环境；
- `__pycache__/`、`.pytest_cache/`、`*.pyc`、`*.egg-info/`、`build/`、`dist/`；
- `hardening/pre_hardening/` 中的本机临时日志与快照；
- `sources/` 下的论文 PDF 和本地文本提取；
- 旧版 `duanmu_ge_lab_source.zip`；
- 任何个人绝对路径。

版权论文应从 `CITATIONS.md` 的官方链接独立获取。clean archive 中的结果是 CPython 3.12 reference environment 最后重建的结果；CPython 3.13 独立验证记录见 `TESTED_ENVIRONMENTS.md`。
