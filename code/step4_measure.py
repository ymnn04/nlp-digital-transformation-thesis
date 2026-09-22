# -*- coding: utf-8 -*-
"""
Step 4 测度计算（企业-年份面板）
===============================
对每个 (企业, 年份) 计算：
  dim_count_d   : 第 d 维度词典词在 MD&A 中的命中次数
  digital_total : 五维度总命中次数
  digital_ratio : 数字化词频占比 = digital_total / n_tokens  (相对量纲，控制篇幅)
  Digital       : 主测度 = ln(1 + digital_total)            (对数化缓解右偏)
输出：data/measure_panel.csv（60企业 x 2020-2024 面板）
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(BASE, "data", "tokens.csv")
DICT = os.path.join(BASE, "output", "step3_词典.csv")
OUT = os.path.join(BASE, "data", "measure_panel.csv")

import importlib.util
spec = importlib.util.spec_from_file_location("s3", os.path.join(BASE, "code", "step3_lexicon.py"))
s3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s3)
LEXICON = s3.LEXICON


def main():
    df = pd.read_csv(TOKENS)
    # 确保 step3 已生成词典（避免重复运行顺序问题）
    if not os.path.exists(DICT):
        s3.main()

    dim_counts = {}
    for dim, kws in LEXICON.items():
        pat = "|".join(kws)
        dim_counts[dim] = df["tokens"].str.count(pat)

    out = df[["stock_code", "firm_name", "industry", "year"]].copy()
    for dim, col in dim_counts.items():
        out[f"cnt_{dim}"] = col.values
    out["digital_total"] = sum(dim_counts.values()).values
    out["n_tokens"] = df["n_tokens"].values
    out["digital_ratio"] = out["digital_total"] / out["n_tokens"].clip(lower=1)
    out["Digital"] = (1 + out["digital_total"]).apply(lambda x: __import__("math").log(x))

    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print("测度面板:", out.shape, " 企业数:", out['stock_code'].nunique())
    print("Digital 均值=%.3f  中位数=%.3f" % (out['Digital'].mean(), out['Digital'].median()))
    print("维度相关样例(人工智能 vs 大数据):",
          round(out['cnt_人工智能'].corr(out['cnt_大数据']), 3))
    print("输出: data/measure_panel.csv")


if __name__ == "__main__":
    main()
