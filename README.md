# 基于年报文本的企业数字化转型测度及其对经营绩效的影响研究 —— NLP 文本测度方法预演论文

> 大连财经学院 · 大数据管理与应用专业 · 课程「预演毕业论文」作业模拟稿

本项目完整演示了**用自然语言处理（NLP）从非结构化文本中构建量化测度**的五步流水线，
并以此写一篇 6000 字以上的毕业论文模拟稿。全部代码、数据、结果与论文均可一键复现。

---

## 一、研究问题与方法

**核心问题**：如何把企业年报中"管理层讨论与分析（MD&A）"文本，量化成可纳入回归的
「企业数字化转型程度」变量，并检验其测量质量？

**技术路线（五步流水线）**：

| 步骤 | 名称 | 关键操作 | 产出 |
|------|------|----------|------|
| Step 1 | 文本获取 | 巨潮资讯网下载年报 / 本仓库用脚本生成演示语料 | `data/raw_corpus.csv` |
| Step 2 | 文本预处理 | 正则清洗 → jieba 分词（加领域自定义词）→ 去停用词 | `data/tokens.csv` |
| Step 3 | 词典与特征构建 | 五维度转型词典词频计数 + TF-IDF 主题抽查 | `output/step3_词典.csv`、`step3_tfidf_top20.csv` |
| Step 4 | 测度计算 | 词频加总 + 对数化 → 企业—年份面板 | `data/measure_panel.csv` |
| Step 5 | 信效度检验与回归 | Cronbach's α、维度相关矩阵、多元回归 | `output/step5_*.csv`、`output/fig*.png` |

**五维度词典**：人工智能 / 大数据 / 云计算 / 区块链 / 数字技术应用（共 53 个示例关键词）。

---

## 二、目录结构

```
nlp-measure-thesis/
├── README.md                       # 本说明
├── .gitignore
├── requirements.txt                # Python 依赖
├── code/                           # 五步流水线 + 文档生成
│   ├── step0_make_demo_corpus.py   # 演示语料/财务数据生成器（可一键复现）
│   ├── step1_acquire.py            # Step1 文本获取（真实数据替换入口）
│   ├── step2_preprocess.py         # Step2 清洗+分词+去停用词
│   ├── step3_lexicon.py            # Step3 词典与TF-IDF
│   ├── step4_measure.py            # Step4 测度计算（面板）
│   ├── step5_validity_regression.py# Step5 信效度+回归+绘图
│   ├── run_all.py                  # 一键跑完五步
│   ├── build_docx.py               # 由论文md生成Word
│   └── stopwords.txt               # 停用词表
├── data/                           # 生成的演示数据
│   ├── raw_corpus.csv              # 原始演示语料
│   ├── tokens.csv                  # 分词结果
│   ├── demo_financials.csv         # 演示财务数据
│   └── measure_panel.csv           # 企业—年份测度面板
├── output/                         # 结果表与插图
│   ├── step3_*.csv  step5_*.csv    # 词典/TF-IDF/信效度/回归结果
│   └── fig1~fig4_*.png            # 年度趋势/分布/相关矩阵/分组比较
└── paper/                          # 论文交付物
    ├── 数字化转型测度模拟论文.docx # Word 版（最终交付）
    ├── 数字化转型测度模拟论文.html # 排版版
    └── 论文正文.md                 # Markdown 源稿
```

---

## 三、本地运行（一键复现）

环境要求：Python 3.10+，并安装依赖：

```bash
pip install -r requirements.txt
# 依赖：pandas numpy matplotlib jieba statsmodels scikit-learn scipy openpyxl python-docx
```

运行五步流水线（自动生成 `data/` 与 `output/` 全部结果）：

```bash
python code/run_all.py
```

生成 Word 论文（依赖 python-docx）：

```bash
python code/build_docx.py
```

---

## 四、结果摘要（演示数据运行结果）

- **信度**：五维度词频的 Cronbach's α = **0.791**（≥0.7，内部一致性可接受）
- **效度**：五维度两两相关系数 0.35—0.54，均 1% 水平显著为正（维度结构效度）
- **回归**：`Digital` 对 ROA 系数 = 0.0096（稳健标准误 0.0016，t = 6.16，***），R² = 0.202

---

## 五、重要说明（请务必阅读）

⚠️ **本文为课程方法模拟稿，非真实实证研究。**
- `data/` 下语料与财务数据由 `step0_make_demo_corpus.py` **脚本随机生成**，仅用于完整演示方法流程，
  结论不构成对任何真实企业的判断。
- 替换为真实数据路径：将 `step1_acquire.py` 中的「演示语料」替换为巨潮资讯网下载的年报 MD&A 文本
  （可用 pdfplumber 提取），并接入真实财务数据，整套五步流水线可直接复用。
- 示例子词典（53 词）规模小于权威词典，正式研究应使用经人工校订的完整词典。

---

## 六、参考文献（GB/T 7714）

1. 吴非, 胡慧芷, 林慧妍, 等. 企业数字化转型与资本市场表现——来自股票流动性的经验证据[J]. 管理世界, 2021, 37(7): 130-144.
2. 袁淳, 肖土盛, 耿春晓, 等. 数字化转型与企业分工：专业化还是纵向一体化[J]. 中国工业经济, 2021(9): 137-155.
3. 赵宸宇, 王文春, 李雪松. 数字化转型如何影响企业全要素生产率[J]. 财贸经济, 2021, 42(7): 114-129.
4. VIAL G. Understanding digital transformation: a review and a research agenda[J]. The Journal of Strategic Information Systems, 2019, 28(2): 118-144.
5. LOUGHRAN T, MCDONALD B. When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks[J]. The Journal of Finance, 2011, 66(1): 35-65.
6. CRONBACH L J. Coefficient alpha and the internal structure of tests[J]. Psychometrika, 1951, 16(3): 297-334.
```
