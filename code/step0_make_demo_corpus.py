# -*- coding: utf-8 -*-
"""
Step 0 生成演示语料与演示财务数据
=================================
真实研究中，本步替换为：从巨潮资讯网 http://www.cninfo.com.cn 下载上市公司
年度报告全文（PDF/HTML），提取"管理层讨论与分析"(MD&A)章节文本。

模拟稿为保证可复现，此处用模板+随机数生成 60 家企业 x 2020-2024 年的
演示语料（模拟MD&A段落）与配套演示财务数据。
注意：所有演示数据仅用于跑通方法流水线，不代表任何真实企业。
"""
import os
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE, "data")
os.makedirs(RAW_DIR, exist_ok=True)

# 行业与数字化倾向（信息技术行业天然数字化语句更多）
INDUSTRIES = {
    "信息技术": 3.0,
    "制造业": 1.5,
    "批发零售": 1.0,
    "房地产": 0.6,
    "农林牧渔": 0.3,
}

# 中性经营语句模板（不含数字化词汇）
NEUTRAL_TEMPLATES = [
    "报告期内，公司实现营业收入{rev}亿元，同比增长{g1}%，主要得益于主营业务产销规模扩大。",
    "公司持续优化产品结构，{prod}业务占比稳步提升，毛利率较上年{pm}个百分点。",
    "面对市场竞争加剧，公司加大渠道建设力度，经销商数量增加{dn}家，覆盖区域进一步扩大。",
    "原材料价格波动对成本端形成一定压力，公司通过集中采购和套期保值部分对冲了成本上行风险。",
    "公司深耕{region}市场，区域市场份额稳中有升，品牌影响力持续增强。",
    "报告期内公司客户结构进一步优化，前五大客户收入占比为{top5}%，客户集中度处于合理区间。",
    "公司积极拓展海外市场，出口业务收入同比增长{g2}%，国际化布局初见成效。",
    "本年度公司人力成本略有上升，管理费用率保持稳定，费用管控成效显现。",
    "公司继续推进产能建设，{prod}项目一期已投产，预计达产后年新增产能{cap}万吨。",
    "报告期内，公司获得高新技术企业资质认定，享受相应税收优惠政策。",
    "公司现金流状况良好，经营活动现金流量净额为{cf}亿元，资产负债结构稳健。",
    "受行业周期影响，部分产品价格有所回落，公司及时调整销售策略，库存水平保持在合理范围。",
    "公司持续加大研发投入，研发费用占营业收入比例为{rd}%，围绕{prod}开展技术攻关。",
    "报告期内公司无重大诉讼仲裁事项，各项经营活动正常开展。",
    "公司高度重视安全生产与环境保护，报告期内未发生重大安全事故。",
    "公司建立健全内部控制系统，治理结构规范，三会运作正常。",
    "下半年公司将围绕年度经营计划，重点做好市场开拓、成本控制与人才梯队建设等工作。",
    "公司主要客户为行业龙头企业，合作关系稳定，应收账款回款情况良好。",
    "报告期内人民币汇率波动加大，公司通过远期结售汇业务降低了汇兑损失。",
    "公司本期新增专利授权{pt}项，累计有效专利{pt2}项，技术储备进一步夯实。",
]

# 数字化语句模板：按五个维度（参考吴非等(2021)维度划分思想）
DIGITAL_TEMPLATES = {
    "人工智能": [
        "公司引入人工智能技术优化{prod}质检环节，缺陷识别准确率显著提升。",
        "公司部署机器学习算法对销售数据进行需求预测，库存周转效率明显改善。",
        "公司建设智能客服系统，应用自然语言处理技术实现工单自动分类。",
        "公司推进计算机视觉技术在生产线上的应用，实现关键工序自动检测。",
        "公司与高校联合开展深度学习算法研究，赋能产品智能设计。",
        "公司上线智能排产系统，通过智能算法优化生产计划排程。",
    ],
    "大数据": [
        "公司建设大数据平台，整合生产、销售与供应链数据，支撑经营决策。",
        "公司开展数据治理体系建设，统一主数据标准，提升数据资产质量。",
        "公司运用数据挖掘技术分析客户行为，实现精准营销。",
        "公司数据中心一期建成投用，具备 PB 级数据存储与计算能力。",
        "公司构建经营分析数据仓库，管理层可实时查看核心经营指标。",
        "公司成立数据中台团队，推动业务数据化、数据业务化。",
    ],
    "云计算": [
        "公司核心业务系统迁移上云，采用混合云架构降低IT运维成本。",
        "公司采购云服务替代传统服务器部署，系统上线周期大幅缩短。",
        "公司基于云平台搭建协同办公体系，跨区域协作效率提升。",
        "公司引入边缘计算设备，实现车间数据的就地处理与实时回传。",
        "公司评估公有云与私有云方案，逐步构建统一算力资源池。",
    ],
    "区块链": [
        "公司探索区块链技术在产品溯源中的应用，实现全流程信息上链。",
        "公司参与行业区块链联盟，推动供应链单证电子化与可信流转。",
        "公司研究基于分布式账本的对账机制，降低交易核对成本。",
        "公司试点数字人民币结算场景，丰富收款渠道。",
        "公司利用智能合约技术自动执行供应商结算条款。",
    ],
    "数字技术应用": [
        "公司制定数字化转型规划，成立数字化管理委员会统筹推进。",
        "公司推进智能制造升级，数字化车间已通过省级认定。",
        "公司建设工业互联网平台，实现设备联网与远程运维。",
        "公司发展电子商务业务，线上渠道收入占比持续提升。",
        "公司推进经营管理信息化，上线新一代ERP系统实现业财一体。",
        "公司应用数字孪生技术对重点产线进行虚拟建模与仿真优化。",
        "公司构建智慧物流体系，仓储分拣自动化水平显著提高。",
        "公司推动业务流程线上化，无纸化办公覆盖全部业务部门。",
    ],
}

FILL = {
    "rev": ["12.6", "28.4", "45.2", "8.9", "63.7", "19.3"],
    "g1": ["8.5", "15.2", "-3.1", "22.7", "5.6", "-1.8"],
    "g2": ["12.1", "30.5", "-6.3", "18.9", "9.4"],
    "prod": ["高端装备", "精细化工产品", "食品饮料", "电子元器件", "纺织服装", "建材"],
    "pm": ["上升1.2", "下降0.8", "持平", "上升2.5", "下降1.5"],
    "dn": ["120", "45", "210", "36", "88"],
    "region": ["华东", "华南", "西南", "华北", "东北"],
    "top5": ["32.5", "41.8", "28.3", "55.1", "36.9"],
    "cf": ["3.2", "8.7", "1.5", "12.4", "5.8"],
    "rd": ["3.2", "5.1", "1.8", "4.4", "2.6"],
    "cap": ["5", "12", "20", "3", "8"],
    "pt": ["8", "15", "3", "22", "11"],
    "pt2": ["56", "120", "38", "210", "85"],
}


def fill_template(tpl):
    out = tpl
    for k, vals in FILL.items():
        out = out.replace("{" + k + "}", random.choice(vals))
    return out


def make_mda(theta, year):
    """theta: 企业数字化倾向强度，决定数字化语句期望数量"""
    # 通用语段：8~12 句
    n_neutral = random.randint(8, 12)
    sents = [fill_template(random.choice(NEUTRAL_TEMPLATES)) for _ in range(n_neutral)]
    # 数字化语句：泊松分布，且随年份有温和上升趋势
    lam = max(theta * (1.0 + 0.15 * (year - 2020)), 0.05)
    for dim, tmpls in DIGITAL_TEMPLATES.items():
        k = np.random.poisson(lam / len(DIGITAL_TEMPLATES) * len(DIGITAL_TEMPLATES) * random.uniform(0.5, 1.5))
        k = min(k, 6)
        for _ in range(k):
            sents.append(random.choice(tmpls))
    random.shuffle(sents)
    return "".join(sents)


def main():
    rows = []
    n_firms = 60
    ind_names = list(INDUSTRIES.keys())
    firm_theta = {}
    for i in range(1, n_firms + 1):
        code = f"DEMO{i:03d}"
        ind = ind_names[(i - 1) % len(ind_names)]
        theta = INDUSTRIES[ind] * np.random.lognormal(0, 0.4)
        firm_theta[code] = (ind, theta)

    for code, (ind, theta) in firm_theta.items():
        for year in range(2020, 2025):
            rows.append({
                "stock_code": code,
                "firm_name": f"演示{code}股份有限公司",
                "industry": ind,
                "year": year,
                "report_type": "年度报告",
                "mda_text": make_mda(theta, year),
                "source_note": "脚本生成演示语料(step0_make_demo_corpus.py)",
            })
    corpus = pd.DataFrame(rows)
    corpus.to_csv(os.path.join(RAW_DIR, "raw_corpus.csv"), index=False, encoding="utf-8-sig")

    # 演示财务数据：ROA 设为与数字化测度正相关 + 噪声（便于演示效标关联效度）
    fin_rows = []
    for code, (ind, theta) in firm_theta.items():
        size0 = np.random.uniform(21, 25)          # ln(总资产)
        lev0 = np.random.uniform(0.2, 0.65)
        age = int(np.random.uniform(5, 25))
        for year in range(2020, 2025):
            size = size0 + 0.05 * (year - 2020) + np.random.normal(0, 0.05)
            lev = float(np.clip(lev0 + np.random.normal(0, 0.03), 0.05, 0.9))
            dig_latent = theta * (1 + 0.15 * (year - 2020))   # 与语料强度同源
            roa = 0.01 + 0.008 * dig_latent + 0.02 * np.random.normal(0, 1)
            grow = 0.05 + 0.02 * dig_latent + 0.08 * np.random.normal(0, 1)
            fin_rows.append({
                "stock_code": code, "year": year, "industry": ind,
                "roa": round(roa, 4), "revenue_growth": round(grow, 4),
                "ln_size": round(size, 3), "leverage": round(lev, 4),
                "firm_age": age + (year - 2020),
                "source_note": "脚本生成演示财务数据，仅用于方法演示",
            })
    pd.DataFrame(fin_rows).to_csv(
        os.path.join(RAW_DIR, "demo_financials.csv"), index=False, encoding="utf-8-sig")

    print(f"演示语料: {corpus.shape[0]} 条 (60家企业 x 2020-2024)")
    print(f"演示财务: 300 条")
    print("输出: data/raw_corpus.csv, data/demo_financials.csv")


if __name__ == "__main__":
    main()
