# 网页分类项目

基于 Prompt + 规则 + 评估的网页分类系统，对比国产模型效果。

## 项目目标

- 对千万级网页进行分类（8大类：时政/经济/军事/社会/科技/体育/娱乐/其它）
- 全本地部署，不走国外 API，不用 VPN
- 不微调模型，纯 Prompt 工程 + 规则
- 输出各国产模型对比结果，供甲方选择

## 验收标准

- Accuracy ≥ 80%
- 提供模型对比报告（准确率、速度、资源占用）

## 项目周期

4 周（详见 docs/timeline.md）

## 目录结构

```
webpage-classification/
├── data/                    # 数据目录
│   ├── raw/                 # 原始 HTML 数据
│   ├── extracted/           # 抽取后的结构化数据
│   ├── sampled/             # 抽样数据集
│   ├── classified/          # 🆕 分类后的数据（按类别存放）
│   │   ├── 时政/
│   │   ├── 经济/
│   │   ├── 军事/
│   │   ├── 社会/
│   │   ├── 科技/
│   │   ├── 体育/
│   │   ├── 娱乐/
│   │   └── 其他/
│   └── labeled/             # 标注数据集
│       ├── train/           # 训练集 (70%)
│       ├── dev/             # 开发集 (10%)
│       └── test/            # 测试集 (20%)
├── models/                  # 🆕 模型目录（存放本地 LLM 模型）
├── src/                     # 源代码
│   ├── extraction/          # HTML 内容抽取模块
│   ├── rules/               # 规则分类模块
│   ├── llm/                 # LLM 推理模块
│   ├── search/              # 🆕 智能搜索模块
│   ├── evaluation/          # 评估模块
│   └── utils/               # 工具函数
├── prompts/                 # Prompt 模板
├── configs/                 # 配置文件
│   ├── config.yaml          # 主配置
│   └── keywords.json        # 关键词库 (4000+ 条)
├── notebooks/               # Jupyter 分析笔记本
├── outputs/                 # 输出结果
│   ├── predictions/         # 模型预测结果
│   ├── reports/             # 评估报告
│   └── figures/             # 图表
├── docs/                    # 文档
│   ├── labeling_guide.md    # 标注规范
│   ├── sampling_plan.md     # 抽样方案
│   └── timeline.md          # 时间线
├── scripts/                 # 脚本
└── requirements.txt         # 依赖
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. HTML 内容抽取
python src/extraction/extractor.py

# 3. 规则分类 baseline
python src/rules/classifier.py

# 4. LLM 分类
python src/llm/classifier.py

# 5. 评估
python src/evaluation/evaluate.py
```

## 🆕 智能搜索功能

用户可以输入查询，系统会自动定位到对应分类，使用 LLM 读取内容并返回 Top 15 相关结果。

### 使用方法

```bash
# 单次查询（禁用 LLM）
python -m src.search.searcher "2020 中国 失业人口" --no-llm

# 单次查询（启用 LLM 增强）
python -m src.search.searcher "2020 中国 失业人口"

# 交互模式
python -m src.search.searcher

# 指定分类
python -m src.search.searcher "央行降息" -c 经济

# 指定返回数量
python -m src.search.searcher "疫情防控" -k 20
```

### 示例输出

```
🔍 查询: 2020 中国 失业人口
📂 自动定位分类: 时政 (置信度: 100.00%)
🔑 匹配关键词: 失业, 人口

============================================================
📊 搜索结果 (共找到 5 条)
============================================================

【1】2020年中国失业人口统计数据发布
    📂 分类: 时政
    🔗 URL: https://www.gov.cn/stats/2020/unemployment
    📊 相关性: 22.50
    📝 国家统计局发布2020年就业统计数据...
```
