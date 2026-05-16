[README.md](https://github.com/user-attachments/files/27854051/README.md)
# CVE 多源描述完整性分析项目

本项目用于复现“CVE 漏洞描述细粒度字段完整性分析”的实验流程，围绕补充前原始 CVE 描述、补充后多源汇总描述，以及人工核验结果，完成 RQ1–RQ4 的统计分析。

\---

## 1\. 项目目标

本项目关注 CVE 描述文本是否充分覆盖漏洞分析所需的细粒度信息。研究对象不是 CVSS/CWE 本身，而是 CVE 描述文本中是否明确表达了若干字段。

整体实验分为四个研究问题：

|研究问题|核心目标|主要分析内容|
|-|-|-|
|RQ1|分析补充前原始 CVE 描述的缺失结构|字段存在率、类别完整性、共同缺失模式|
|RQ2|分析多源补充是否提升描述完整性|before/after 配对比较、Gain、FillRate、McNemar 检验、置信区间|
|RQ3|分析补充后仍然残余缺失的字段|residual 排序、高 residual 字段抽样、人工归因校准|
|RQ4|分析自动标注和实验流程中的偏差|n10 复核、漏识别、边界偏差、残余高估率、偏差指标|

\---

## 2\. 项目目录结构

推荐项目结构如下：

```text
cve\_description\_study\_clean/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   └── processed/
│       └── .gitkeep
│
├── outputs/
│   └── .gitkeep
│
└── src/
    ├── common/
    │   ├── \_\_init\_\_.py
    │   ├── config.py
    │   ├── fields.py
    │   └── io\_utils.py
    │
    ├── rq1/
    │   ├── \_\_init\_\_.py
    │   ├── rq1\_field\_metrics.py
    │   ├── rq1\_category\_metrics.py
    │   └── rq1\_comissing\_analysis.py
    │
    ├── rq2/
    │   ├── \_\_init\_\_.py
    │   ├── rq2\_build\_paired\_dataset.py
    │   ├── rq2\_field\_metrics.py
    │   ├── rq2\_category\_metrics.py
    │   ├── rq2\_sample\_metrics.py
    │   ├── rq2\_statistical\_tests.py
    │   └── rq2\_confidence\_intervals.py
    │
    ├── rq3/
    │   ├── \_\_init\_\_.py
    │   ├── rq3\_residual\_metrics.py
    │   ├── rq3\_sample\_high\_residual.py
    │   └── rq3\_manual\_calibration.py
    │
    └── rq4/
        ├── \_\_init\_\_.py
        ├── rq4\_build\_bias\_input.py
        ├── rq4\_manual\_review\_summary.py
        └── rq4\_bias\_metrics.py
```

\---

## 3\. 各目录说明

### 3.1 `data/processed/`

`data/processed/` 用于存放数据文件。项目脚本默认主要读取这个目录。

最少需要放入以下文件：

```text
5000cve\_before.xlsx
cve\_after.xlsx
cve\_description.json
```

如果需要运行 RQ3、RQ4 的人工校准和偏差分析，还需要放入人工核验文件：

```text
RQ2\_n10\_manual\_review.xlsx
RQ3\_manual\_review.xlsx
```

\---

### 3.2 `outputs/`

`outputs/` 是脚本自动生成结果的目录。运行代码后，所有统计表、配对表、抽样表和偏差分析表都会输出到这里。

不建议手动把原始数据放入 `outputs/`。该目录中的结果通常可以重新生成，因此默认不上传 GitHub。

\---

### 3.3 `src/common/`

`src/common/` 是公共代码目录，存放各个 RQ 都会用到的配置、字段映射和工具函数。

|文件|作用|
|-|-|
|`config.py`|统一管理项目根目录、数据目录和输出目录|
|`fields.py`|统一管理 24 个细粒度字段、中文名、一级类别映射|
|`io\_utils.py`|提供通用 Excel 读写、目录创建、0/1 字段清洗等函数|
|`\_\_init\_\_.py`|让该目录可以被 Python 当作包导入|

\---

## 4\. 字段体系说明

本项目使用 6 个一级类别、24 个细粒度字段来判断 CVE 描述是否完整。

### 4.1 漏洞类型

|字段名|中文含义|
|-|-|
|`has\_specific\_vuln\_type`|具体漏洞类型|
|`has\_big\_category`|大类漏洞|
|`has\_core\_feature`|核心特征|
|`has\_trigger\_condition`|触发条件|

### 4.2 根本原因

|字段名|中文含义|
|-|-|
|`has\_specific\_error\_point`|具体错误点|
|`has\_error\_type\_attribution`|错误类型归属|
|`has\_direct\_program\_anomaly`|直接程序异常|

### 4.3 受影响产品

|字段名|中文含义|
|-|-|
|`has\_vendor\_or\_maintainer`|产品开发主体|
|`has\_product\_name`|产品名称|
|`has\_affected\_version`|受影响版本|
|`has\_affected\_component`|受影响组件|
|`has\_environment\_constraint`|影响环境|

### 4.4 攻击者类型

|字段名|中文含义|
|-|-|
|`has\_attacker\_identity\_type`|攻击者身份类型|
|`has\_attacker\_privilege\_traits`|攻击者权限特征|
|`has\_attack\_operation\_method`|攻击操作方式|
|`has\_precondition\_constraints`|前置约束条件|

### 4.5 影响

|字段名|中文含义|
|-|-|
|`has\_core\_impact\_type`|核心影响类型|
|`has\_specific\_harm\_action`|具体危害行为|
|`has\_harm\_constraints`|危害约束条件|
|`has\_followon\_escalation\_harm`|后续衍生危害|

### 4.6 攻击载体

|字段名|中文含义|
|-|-|
|`has\_vector\_general\_class`|载体大类|
|`has\_vector\_specific\_form`|载体具体形态|
|`has\_vector\_delivery\_method`|载体传递方式|
|`has\_specific\_attack\_point`|具体受攻击点|

\---

## 5\. 环境配置

建议使用 Python 3.9 或更高版本。

安装依赖：

```bash
pip install -r requirements.txt
```

`requirements.txt` 中通常包含：

```text
pandas
numpy
openpyxl
xlsxwriter
scipy
pyyaml
```

如果不使用 `yaml` 配置文件，`pyyaml` 不是必须的。

\---

## 6\. 输入文件要求

### 6.1 `5000cve\_before.xlsx`

该文件是补充前的 CVE 描述基线表。

建议放置路径：

```text
data/processed/5000cve\_before.xlsx
```

建议包含以下基础列：

```text
cve\_id
cwe\_id
description
```

同时需要包含 24 个 `has\_\*` 字段，例如：

```text
has\_specific\_vuln\_type
has\_big\_category
has\_core\_feature
has\_trigger\_condition
...
has\_specific\_attack\_point
```

字段值应为 `0` 或 `1`。

\---

### 6.2 `cve\_after.xlsx`

该文件是多源补充后的 CVE 描述状态表。

建议放置路径：

```text
data/processed/cve\_after.xlsx
```

建议包含：

```text
cve\_id
description
24 个 has\_\* 字段
```

为了 RQ2 能顺利配对，`cve\_after.xlsx` 中的 `cve\_id` 应能在 `5000cve\_before.xlsx` 中找到对应记录。

\---

### 6.3 `cve\_description.json`

该文件存放每条 CVE 的多源描述信息。

建议放置路径：

```text
data/processed/cve\_description.json
```

该文件主要用于：

```text
统计 source\_count
提取 source\_type
辅助 RQ3 抽样时提供 after/source 文本节选
辅助 RQ4 构建偏差分析输入表
```

\---

## 7\. 人工核验文件要求

本项目中 RQ3 和 RQ4 部分涉及人工核验。自动脚本无法完全替代人工判断，因此需要手动填写部分表格。

\---

### 7.1 RQ2 n10 专项复核表

文件建议命名为：

```text
data/processed/RQ2\_n10\_manual\_review.xlsx
```

该文件用于复核 RQ2 中出现的异常下降情况：

```text
before = 1, after = 0
```

这种转移称为 `n10`。理论上，多源补充后字段不应比补充前更少，因此 n10 需要专项复核。

核心 Sheet 建议命名为：

```text
n10\_detail
```

建议包含以下列：

```text
cve\_id
field
字段中文
review\_result
建议before值
建议after值
review\_reason
before\_excerpt
after\_excerpt
相似度
```

其中 `review\_result` 建议填写以下类型之一：

|取值|含义|
|-|-|
|`before过宽标注`|补充前标注过宽，before 原本不应为 1|
|`after漏标`|补充后文本中有证据，但 after 被错误标为 0|
|`边界问题`|字段定义边界模糊，严格/宽松口径不同|
|`样本配对异常`|before/after 不是同一有效样本或文本配对存在问题|

\---

### 7.2 RQ3 高 residual 人工归因表

文件建议命名为：

```text
data/processed/RQ3\_manual\_review.xlsx
```

该文件用于复核补充后仍被自动判为缺失的高 residual 字段样本。

核心 Sheet 可以命名为：

```text
Sheet1
```

或在脚本中改成你自己的 Sheet 名。

建议包含以下列：

```text
cve\_id
field\_key
字段
一级类别
after原判
manual\_after\_status
attribution\_type
evidence\_text
comment
```

其中：

#### `manual\_after\_status`

人工复核后判断该字段在 after 描述中是否存在。

|取值|含义|
|-|-|
|`0`|after 描述中没有明确表达该字段|
|`1`|after 描述中有明确、直接、可定位的表达|

#### `attribution\_type`

用于说明 automatic residual 的原因。

|类型|含义|RQ4 对应偏差|
|-|-|-|
|A|真实残余缺失，after 合并描述中确实没有明确表达|非方法误差|
|B|隐式/边界模糊，有弱线索但严格口径不能判 1|E4 边界偏差|
|C|粒度不匹配，文本有相关信息但达不到字段定义粒度|E2/E4 粒度或归类边界偏差|
|D|自动化/标注漏识别，after 中已有明确证据但原判为 0|E1 字段存在性漏判|

#### `evidence\_text`

填写支持人工判断的 after 原文证据片段。

如果是 A 类真实残余缺失，可以填写：

```text
未发现明确表达
```

#### `comment`

填写简短备注，例如：

```text
仅说明漏洞类型，未明确攻击者权限
```

或：

```text
描述中有相关线索，但粒度不足，不能严格判为 1
```

\---

## 8\. 运行方式

分步骤运行

如果希望逐步检查结果，建议分步骤运行。

#### RQ1

```bash
python src/rq1/rq1\_field\_metrics.py
python src/rq1/rq1\_category\_metrics.py
python src/rq1/rq1\_comissing\_analysis.py
```

#### RQ2

```bash
python src/rq2/rq2\_build\_paired\_dataset.py
python src/rq2/rq2\_field\_metrics.py
python src/rq2/rq2\_category\_metrics.py
python src/rq2/rq2\_sample\_metrics.py
python src/rq2/rq2\_statistical\_tests.py
python src/rq2/rq2\_confidence\_intervals.py
```

#### RQ3

```bash
python src/rq3/rq3\_residual\_metrics.py
python src/rq3/rq3\_sample\_high\_residual.py
```

然后需要人工填写抽样表。

填写完成后，再运行：

```bash
python src/rq3/rq3\_manual\_calibration.py
```

#### RQ4

```bash
python src/rq4/rq4\_build\_bias\_input.py
python src/rq4/rq4\_manual\_review\_summary.py
python src/rq4/rq4\_bias\_metrics.py
```

\---

## 9\. 各脚本说明

### 9.1 RQ1 脚本

#### `rq1\_field\_metrics.py`

作用：计算补充前原始 CVE 描述中每个细粒度字段的存在率和缺失率。

输入：

```text
data/processed/5000cve\_before.xlsx
```

输出：

```text
outputs/rq1\_field\_metrics.xlsx
```

主要 Sheet：

```text
field\_metrics
```

\---

#### `rq1\_category\_metrics.py`

作用：计算六个一级类别的平均存在率、全存在占比、全缺失占比、缺失至少一半占比，以及每条 CVE 在各类别内的缺失项数。

输入：

```text
data/processed/5000cve\_before.xlsx
```

输出：

```text
outputs/rq1\_category\_metrics.xlsx
```

主要 Sheet：

```text
category\_metrics
missing\_distribution
per\_cve\_category
```

\---

#### `rq1\_comissing\_analysis.py`

作用：分析字段之间是否存在共同缺失现象，计算共同缺失数、共同缺失率、Jaccard 和 phi 系数。

输入：

```text
data/processed/5000cve\_before.xlsx
```

输出：

```text
outputs/rq1\_comissing\_analysis.xlsx
```

主要 Sheet：

```text
all\_field\_pairs
top\_phi\_pairs
phi\_matrix
comissing\_rate\_matrix
```

\---

### 9.2 RQ2 脚本

#### `rq2\_build\_paired\_dataset.py`

作用：按 `cve\_id` 将 before 表和 after 表进行内连接，构建 before/after 配对样本。

输入：

```text
data/processed/5000cve\_before.xlsx
data/processed/cve\_after.xlsx
```

输出：

```text
outputs/rq2\_paired\_dataset.xlsx
```

主要 Sheet：

```text
paired\_dataset
pairing\_summary
```

\---

#### `rq2\_field\_metrics.py`

作用：计算每个字段的 before 完整性、after 完整性、Gain、FillRate、ResidualMiss、DropRate 和 2×2 转移表。

输出：

```text
outputs/rq2\_field\_metrics.xlsx
```

主要 Sheet：

```text
field\_metrics
abnormal\_drop\_fields
```

\---

#### `rq2\_category\_metrics.py`

作用：按六个一级类别汇总 before/after 平均完整性、类别级 Gain、类别内部缺失项变化。

输出：

```text
outputs/rq2\_category\_metrics.xlsx
```

主要 Sheet：

```text
category\_metrics
missing\_distribution
category\_sample\_gain
```

\---

#### `rq2\_sample\_metrics.py`

作用：从样本级分析每条 CVE 补充前后覆盖字段数的变化。

输出：

```text
outputs/rq2\_sample\_metrics.xlsx
```

主要 Sheet：

```text
sample\_metrics
gain\_distribution
stratified\_gain
```

\---

#### `rq2\_statistical\_tests.py`

作用：对每个字段执行 McNemar 检验，并提取 n10 异常下降字段和样本。

输出：

```text
outputs/rq2\_statistical\_tests.xlsx
```

主要 Sheet：

```text
mcnemar\_results
abnormal\_drop\_fields
abnormal\_drop\_samples
category\_review
```

\---

#### `rq2\_confidence\_intervals.py`

作用：补充字段级、类别级和样本级增益的 95% 置信区间。

输出：

```text
outputs/rq2\_confidence\_intervals.xlsx
```

主要 Sheet：

```text
field\_ci
category\_ci
sample\_ci
```

\---

### 9.3 RQ3 脚本

#### `rq3\_residual\_metrics.py`

作用：基于 after 字段状态计算每个字段的 residual 残余缺失率，并识别高 residual 字段。

输入：

```text
outputs/rq2\_paired\_dataset.xlsx
data/processed/cve\_description.json
```

输出：

```text
outputs/rq3\_residual\_metrics.xlsx
```

主要 Sheet：

```text
after\_status
field\_residual
high\_residual\_fields
category\_residual
source\_count\_aux
```

\---

#### `rq3\_sample\_high\_residual.py`

作用：从高 residual 字段中抽取人工核验样本。

输出：

```text
outputs/rq3\_high\_residual\_samples.xlsx
```

主要 Sheet：

```text
manual\_samples
field\_sample\_summary
```

该文件生成后，需要人工填写。建议填写完成后另存为：

```text
data/processed/RQ3\_manual\_review.xlsx
```

\---

#### `rq3\_manual\_calibration.py`

作用：读取人工核验结果，统计 A/B/C/D 归因分布，并计算人工校准后的 residual。

输入：

```text
data/processed/RQ3\_manual\_review.xlsx
outputs/rq3\_residual\_metrics.xlsx
```

输出：

```text
outputs/rq3\_manual\_calibration.xlsx
```

主要 Sheet：

```text
overall\_attribution
by\_field
by\_category
manual\_samples
```

\---

### 9.4 RQ4 脚本

#### `rq4\_build\_bias\_input.py`

作用：整合 RQ2 配对结果、n10 复核、RQ3 人工归因结果，构建 CVE×字段级偏差分析输入表。

输入：

```text
outputs/rq2\_paired\_dataset.xlsx
outputs/rq2\_statistical\_tests.xlsx
data/processed/RQ2\_n10\_manual\_review.xlsx
data/processed/RQ3\_manual\_review.xlsx
outputs/rq3\_manual\_calibration.xlsx
```

输出：

```text
outputs/rq4\_bias\_input.xlsx
```

主要 Sheet：

```text
bias\_input
field\_metadata
```

\---

#### `rq4\_manual\_review\_summary.py`

作用：汇总 RQ2 n10 复核和 RQ3 人工归因结果，形成 RQ4 的人工核验证据。

输出：

```text
outputs/rq4\_manual\_review\_summary.xlsx
```

主要 Sheet：

```text
rq3\_attribution\_summary
rq3\_by\_field
rq3\_by\_category
n10\_review\_summary
n10\_by\_field
n10\_by\_category
```

\---

#### `rq4\_bias\_metrics.py`

作用：计算 RQ4 的核心偏差指标，包括 E1/E2/E4、真实残余比例、residual 高估率、n10 方法性解释率等。

输出：

```text
outputs/rq4\_bias\_metrics.xlsx
```

主要 Sheet：

```text
bias\_metrics
rq3\_field\_bias
n10\_bias
```

\---

## 输出文件汇总

|文件|说明|
|-|-|
|`rq1\_field\_metrics.xlsx`|RQ1 字段级存在率|
|`rq1\_category\_metrics.xlsx`|RQ1 类别级缺失结构|
|`rq1\_comissing\_analysis.xlsx`|RQ1 字段共同缺失分析|
|`rq2\_paired\_dataset.xlsx`|RQ2 before/after 配对样本|
|`rq2\_field\_metrics.xlsx`|RQ2 字段级补充效果|
|`rq2\_category\_metrics.xlsx`|RQ2 类别级补充效果|
|`rq2\_sample\_metrics.xlsx`|RQ2 样本级补充收益|
|`rq2\_statistical\_tests.xlsx`|RQ2 McNemar 检验和 n10 提取|
|`rq2\_confidence\_intervals.xlsx`|RQ2 置信区间|
|`rq3\_residual\_metrics.xlsx`|RQ3 residual 指标|
|`rq3\_high\_residual\_samples.xlsx`|RQ3 高 residual 人工抽样表|
|`rq3\_manual\_calibration.xlsx`|RQ3 人工归因校准结果|
|`rq4\_bias\_input.xlsx`|RQ4 偏差分析输入长表|
|`rq4\_manual\_review\_summary.xlsx`|RQ4 人工核验汇总|
|`rq4\_bias\_metrics.xlsx`|RQ4 偏差指标计算结果|



