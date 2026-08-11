# Tested Environments

`pyproject.toml` 声明支持范围；本文件只记录本轮真实执行过的环境，不把尚未运行的 CI 配置伪装成验证结果。

| Platform | Python | NumPy | SciPy | pytest | Matplotlib | PyYAML | Tests | Compile | Reproducibility suite | Final audit |
|---|---:|---:|---:|---:|---:|---:|---|---|---|---|
| Windows 11 | CPython 3.12.13 | 2.5.2 | 1.18.0 | 9.1.1 | 3.11.1 | 6.0.3 | 113 passed, 0 failed | passed | `REPRODUCIBILITY_SUITE_SUCCESS` | `FINAL_AUDIT_PASSED` |
| Windows 11 | CPython 3.13.0 | 2.5.2 | 1.18.0 | 9.1.1 | 3.11.1 | 6.0.3 | 113 passed, 0 failed | passed | `REPRODUCIBILITY_SUITE_SUCCESS` | `FINAL_AUDIT_PASSED` |

两行均在同一台 Windows 机器的独立虚拟环境中实际执行。3.13 环境还实际运行了 baseline、Examples 1/3 和 Theorems 3-4 mapping 的 CI smoke commands。

GitHub Actions 已配置 Ubuntu 上 CPython 3.11、3.12、3.13 矩阵，步骤包括安装、pytest、compileall、baseline、关键论文复现、完整 suite 和 strict final audit。当前没有可引用的远程 workflow run，因此只能写 **CI CONFIGURED**，不能写 CI verified；Python 3.11 也不能列为本地已测试环境。

`requirements-tested.txt` 固定 3.12 参考环境的精确依赖版本。3.13 本轮解析到了相同的直接和传递版本，但这不意味着该 pins 文件覆盖所有 OS 或未来解释器。
