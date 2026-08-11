# Duanmu GE Lab

`Duanmu GE Lab` 是一个可复现的**有限模型论文复现、均衡搜索与独立数值诊断框架**，围绕 Anderson 与 Duanmu 的配额和排放税一般均衡研究开发。当前项目包含解析基准、有限生产与人口加权组件、有符号价格、论文 Examples 1-6 的专用实现、多重候选实验、政策扫描和严格 candidate diagnostics。

它不是通用一般均衡求解器，也不实现测度经济、综合外部性或非标准分析的数学证明。完整边界见 [Scope and Limitations](docs/SCOPE_AND_LIMITATIONS.md)。

## Implemented

- 纯交换与生产经济，显式净产出、企业持股和收入分解；
- candidate 资源会计与独立重新优化的消费者/企业最优性诊断；
- 与社会福利权重分离的人口权重聚合；
- signed-L1 与 numeraire 坐标、有符号价格和逐商品出清规则；
- 负价格坏品与显式消费集合；
- 论文 Definitions 3.1-3.5 的配额会计和 Definitions 4.1-4.3 的税收会计；
- Anderson-Duanmu Examples 1-6 的有限模型专用复现；
- Theorems 3-4 映射的数值一致性核对；
- deterministic、random、continuation 多起点和验证候选聚类；
- 税率到排放集合、配额目标到配额价格集合的参数扫描；
- 固定排放下的配额产权分配实验；
- construction-specific 的有限加权坏品吸收实验；
- YAML 运行参数、复现元数据、研究图和严格最终审计。

## Claim Boundaries

- `VERIFIED_CANDIDATE` 表示一个有限 candidate 在记录的容差下通过全部已实现诊断，不表示一般存在性证明。
- `DISCOVERED_N_VERIFIED_CANDIDATE_CLUSTERS` 只描述给定搜索协议发现的候选簇，不表示恰有 `N` 个均衡。
- Example 4 的 `NO_EQUILIBRIUM` 来自论文理论；数值搜索零发现本身不是证明。
- Milestone 11 是 paper-inspired finite-grid experiment。聚合量稳定主要来自该线性中点构造，不是连续经济收敛定理或 uniform-integrability 验证。
- 项目没有一般 comprehensive-externality preference interface，没有 Loeb measure 或 hyperfinite implementation，也没有自动计算“最优碳政策”。

## Installation

`pyproject.toml` 给出支持的依赖范围；`requirements-tested.txt` 记录一套实际验证过的 Windows/CPython 参考环境。参考 pins 不代表所有操作系统都已验证。

Cross-platform setup:

```text
cd <path-to-project>/duanmu_ge_lab
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q src scripts paper_replications
```

Windows PowerShell 无需激活虚拟环境：

```powershell
cd <path-to-project>\duanmu_ge_lab
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall -q src scripts paper_replications
```

POSIX 无需激活虚拟环境：

```bash
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

安装精确参考环境时，先运行 `python -m pip install -r requirements-tested.txt`，再运行 `python -m pip install -e . --no-deps`。

## Smoke Tests

最小解析基准：

```text
python scripts/run_baseline.py
```

从头重建全部 required 实验和图；任一 expected status 不匹配时返回非零退出码：

```text
python scripts/run_reproducibility_suite.py
python scripts/run_final_audit.py
```

Windows 可把上述 `python` 替换为 `.\.venv\Scripts\python.exe`。

## Configuration Boundary

YAML 驱动已暴露的实验参数，例如配额、税率、产权制度、初值、网格、人口规模、随机种子和 solver settings：

```text
python scripts/run_experiment.py --config configs/paper/example_3.yaml
python scripts/run_experiment.py --config configs/experiments/tax_quota_sweeps.yaml
```

论文例子的商品结构、偏好、技术和方程约化仍由 paper-specific Python builders/solvers 表达。项目不能仅凭任意 YAML 自动生成新模型或求解器。

## Research Results

- Examples 1-2：解析价格、配置、利润和产权分配逐项比较并通过完整诊断；
- Example 3：在论文税率下稳定发现三条验证候选分支并匹配 Table I；
- Example 4：分别保存论文非存在状态和计算预检；
- Example 5：同一目标出现不同税率/配额价格候选，匹配 Tables II-III；
- Example 6：数值核对税与配额在目标保证上的差异。

关键图：[tax-emission correspondence](figures/tax_emission_correspondence.png)。图的 caption 与源 JSON 见 [figures/README.md](figures/README.md)。

## Navigation

- [Professor demo](PROFESSOR_DEMO.md)
- [Final research report](REPORT.md)
- [Post-hardening audit](FINAL_AUDIT.md)
- [Hardening report](FINAL_HARDENING_REPORT.md)
- [Tested environments](TESTED_ENVIRONMENTS.md)
- [Tolerance audit](TOLERANCE_AUDIT.md)
- [Paper parameter audit](PAPER_PARAMETER_AUDIT.md)
- [Research claim audit](RESEARCH_CLAIM_AUDIT.md)
- [Collaborator guide](COLLABORATOR_GUIDE.md)
- [Citations and source locations](CITATIONS.md)
- [Current research questions](OPEN_QUESTIONS.md)
- [Mathematical specifications](docs/)
- [Machine-readable results](results/)

CI is configured for CPython 3.11, 3.12, and 3.13 in `.github/workflows/tests.yml`. Until a remote workflow run is available, this is accurately described as **CI CONFIGURED**, not CI verified.
