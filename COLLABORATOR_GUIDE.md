# Collaborator Guide

## 接入一个新的有限模型需要什么

理论研究者应先提供：

1. 商品及每个坐标的经济含义，包括 goods/bads 和价格符号约束；
2. 消费者集合、禀赋、消费集、偏好或可计算选择规则；
3. 企业、生产集、所有权份额及利润分配规则；
4. quota、tax、rebate 或其他政策的精确会计恒等式；
5. 价格规范化、numeraire 与论文坐标之间的转换；
6. candidate 必须满足的资源、预算、最优性和互补条件；
7. 已知解析解、理论边界、反例或表格值，以及准确来源；
8. 允许的搜索区域、初值信息和可接受的数值误差依据。

## 程序接入步骤

先把模型翻译成现有 core/policy 对象能够表达的有限结构；若数学结构不同，则编写最小的 paper-specific builder、candidate solver 和 diagnostics。随后把论文参数与计算参数分开写入 YAML，增加解析或高精度基准测试，再注册精确的成功/失败状态并加入 reproducibility suite。

新结果必须保留失败运行、记录随机种子和搜索协议，并用 candidate 自身的量做资源与政策会计。重求最优量只用于比较 utility/profit gap。

## 当前边界

本包不会从任意数学描述或任意 YAML 自动生成均衡求解器。新的模型仍需要 model-specific mathematical translation；若涉及不完全偏好、综合外部性、无限维或测度经济，还需要超出当前有限框架的新理论与软件设计。
