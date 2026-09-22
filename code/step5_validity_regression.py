# -*- coding: utf-8 -*-
"""
Step 5 信效度检验与实证回归
===========================
1) 信度检验：以五个维度词频为"题项"，计算 Cronbach's alpha；
2) 效度检验：
   - 内容维度结构：五维度两两 Pearson 相关（维度间应正相关，指向同一潜在构念）
   - 效标关联效度：Digital 与演示 ROA 的回归（真实研究应替换为真实财务数据）
3) 实证回归：ROA = a + b*Digital + Controls + 年份固定效应，statsmodels OLS
4) 输出：描述性统计表、信效度表、回归表、图1-图4
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANEL = os.path.join(BASE, "data", "measure_panel.csv")
FIN = os.path.join(BASE, "data", "demo_financials.csv")
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

DIMS = ["人工智能", "大数据", "云计算", "区块链", "数字技术应用"]


def cronbach_alpha(X: pd.DataFrame) -> float:
    """Cronbach's alpha：X 为 n 个观测 x k 个题项"""
    k = X.shape[1]
    item_var = X.var(axis=0, ddof=1).sum()
    total_var = X.sum(axis=1).var(ddof=1)
    return k / (k - 1) * (1 - item_var / total_var)


def main():
    panel = pd.read_csv(PANEL)
    fin = pd.read_csv(FIN)
    df = panel.merge(fin, on=["stock_code", "year", "industry"], how="inner")

    # ---------- 描述性统计 ----------
    desc = df[["Digital", "digital_total", "digital_ratio", "roa",
               "revenue_growth", "ln_size", "leverage", "firm_age"]].describe().T
    desc.columns = ["样本量", "均值", "标准差", "最小值", "25%", "中位数", "75%", "最大值"]
    desc.round(4).to_csv(os.path.join(OUT, "step5_描述性统计.csv"), encoding="utf-8-sig")

    # ---------- 信度：Cronbach's alpha ----------
    alpha = cronbach_alpha(df[[f"cnt_{d}" for d in DIMS]])
    print(f"Cronbach's alpha = {alpha:.3f}")

    # ---------- 效度：维度相关矩阵 ----------
    corr = df[[f"cnt_{d}" for d in DIMS]].corr()
    corr.round(3).to_csv(os.path.join(OUT, "step5_维度相关矩阵.csv"), encoding="utf-8-sig")

    # ---------- 回归（效标关联效度 + 实证检验） ----------
    df["year_c"] = df["year"] - 2020
    m1 = smf.ols("roa ~ Digital", data=df).fit(cov_type="HC1")
    m2 = smf.ols("roa ~ Digital + ln_size + leverage + firm_age + C(year_c)",
                 data=df).fit(cov_type="HC1")
    m3 = smf.ols("revenue_growth ~ Digital + ln_size + leverage + firm_age + C(year_c)",
                 data=df).fit(cov_type="HC1")

    def row(m, name):
        return {"模型": name,
                "Digital系数": round(m.params["Digital"], 4),
                "稳健标准误": round(m.bse["Digital"], 4),
                "t值": round(m.tvalues["Digital"], 2),
                "p值": round(m.pvalues["Digital"], 4),
                "R2": round(m.rsquared, 3), "N": int(m.nobs)}

    reg = pd.DataFrame([row(m1, "(1) ROA基准"), row(m2, "(2) ROA+控制+年份FE"),
                        row(m3, "(3) 营收增长+控制+年份FE")])
    reg.to_csv(os.path.join(OUT, "step5_回归结果.csv"), index=False, encoding="utf-8-sig")
    print(reg.to_string(index=False))

    # ---------- 图1：测度年度趋势（分行业） ----------
    trend = df.groupby(["year", "industry"])["Digital"].mean().unstack()
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    xs = trend.index.astype(int)
    for col in trend.columns:
        ax.plot(xs, trend[col], marker="o", label=col)
    ax.set_xlabel("年份"); ax.set_ylabel("数字化转型测度均值 ln(1+词频)")
    ax.set_title("图1  企业数字化转型测度的年度趋势（分行业）")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig1_年度趋势.png")); plt.close(fig)

    # ---------- 图2：测度分布 ----------
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=150)
    ax.hist(df["Digital"], bins=25, color="#4C72B0", edgecolor="white")
    ax.axvline(df["Digital"].mean(), color="red", ls="--",
               label=f"均值 {df['Digital'].mean():.2f}")
    ax.set_xlabel("数字化转型测度 ln(1+词频)"); ax.set_ylabel("企业-年份数")
    ax.set_title("图2  数字化转型测度的分布")
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig2_测度分布.png")); plt.close(fig)

    # ---------- 图3：维度相关热力图 ----------
    fig, ax = plt.subplots(figsize=(6.4, 5.4), dpi=150)
    im = ax.imshow(corr.values, cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(DIMS)), DIMS, rotation=30, ha="right")
    ax.set_yticks(range(len(DIMS)), DIMS)
    for i in range(len(DIMS)):
        for j in range(len(DIMS)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                    color="white" if corr.values[i, j] > 0.6 else "#1f3b63")
    ax.set_title("图3  五维度词频相关矩阵（效度佐证）")
    fig.colorbar(im, shrink=0.85)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig3_维度相关.png")); plt.close(fig)

    # ---------- 图4：数字化高低的ROA分组箱线 ----------
    df["dig_group"] = pd.qcut(df["Digital"], 3, labels=["低", "中", "高"])
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=150)
    data_box = [df.loc[df["dig_group"] == g, "roa"] for g in ["低", "中", "高"]]
    ax.boxplot(data_box, tick_labels=["低数字化", "中数字化", "高数字化"])
    ax.set_ylabel("ROA（演示数据）"); ax.grid(alpha=0.3)
    ax.set_title("图4  不同数字化水平的ROA分组比较")
    fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig4_分组比较.png")); plt.close(fig)

    # ---------- 信效度汇总 ----------
    summary = pd.DataFrame([
        {"检验项": "Cronbach's alpha（五维度词频为题项）", "结果": round(alpha, 3),
         "判断标准": "≥0.7 为可接受", "结论": "通过" if alpha >= 0.7 else "未通过"},
        {"检验项": "维度间相关系数范围", "结果": f"{corr.values[np.triu_indices(5,1)].min():.2f} ~ "
                     f"{corr.values[np.triu_indices(5,1)].max():.2f}",
         "判断标准": "维度间显著正相关", "结论": "见 step5_维度相关矩阵.csv"},
        {"检验项": "效标关联效度(Digital→ROA, 模型2)",
         "结果": f"b={m2.params['Digital']:.4f}, p={m2.pvalues['Digital']:.4f}",
         "判断标准": "系数方向符合理论预期且显著", "结论": "见 step5_回归结果.csv"},
    ])
    summary.to_csv(os.path.join(OUT, "step5_信效度检验汇总.csv"),
                   index=False, encoding="utf-8-sig")
    print("输出: 描述统计/信效度/回归 csv + fig1~fig4 图")


if __name__ == "__main__":
    main()
