# -*- coding: utf-8 -*-
"""
Step 3 词典构建与特征扩展
========================
主测度采用"词典法"：参考吴非等(2021)《企业数字化转型与资本市场表现——来自股票
流动性水平的经验证据》（《管理世界》）的维度划分思想，将企业数字化转型文本词汇
分为五个维度，整理"示例子词典"（真实研究应替换为完整权威词典，本仓库附词典仅作
方法示范，词项规模小于原文）。

五维度：
  人工智能 / 大数据 / 云计算 / 区块链 / 数字技术应用

同时给出 TF-IDF 高频词抽查（方法稳健性佐证：高频词应集中于数字化主题词）。
"""
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKENS = os.path.join(BASE, "data", "tokens.csv")
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)

# 示例子词典（参考吴非等(2021)维度思想整理，非完整版）
LEXICON = {
    "人工智能": ["人工智能", "机器学习", "深度学习", "神经网络", "智能算法",
              "自然语言处理", "计算机视觉", "人脸识别", "语音识别", "智能机器人", "AI"],
    "大数据": ["大数据", "数据挖掘", "数据分析", "数据资产", "数据中心", "数据治理",
            "数据中台", "数据仓库", "数据安全", "数据驱动"],
    "云计算": ["云计算", "云平台", "云服务", "云存储", "边缘计算", "算力",
            "混合云", "私有云", "公有云"],
    "区块链": ["区块链", "智能合约", "分布式账本", "数字货币", "数字人民币",
            "加密技术", "链上"],
    "数字技术应用": ["数字化转型", "数字经济", "互联网+", "信息化", "智能制造",
               "数字孪生", "电子商务", "跨境电商", "线上化", "智慧物流",
               "智慧城市", "工业互联网", "数字管理", "数字技术", "智能化", "业财一体"],
}


def main():
    df = pd.read_csv(TOKENS)
    # 1) TF-IDF 高频词抽查（佐证文本聚焦主题）
    vec = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    X = vec.fit_transform(df["tokens"].astype(str))
    mean_tfidf = X.mean(axis=0).A1
    vocab = vec.get_feature_names_out()
    top = pd.DataFrame({"word": vocab, "tfidf": mean_tfidf}).sort_values(
        "tfidf", ascending=False).head(20)
    top.to_csv(os.path.join(OUT, "step3_tfidf_top20.csv"), index=False, encoding="utf-8-sig")
    print("TF-IDF Top20 词：", ", ".join(top["word"].head(10).tolist()))

    # 2) 词典落地：保存为 csv 供复用
    rows = [{"dimension": d, "keyword": kw} for d, kws in LEXICON.items() for kw in kws]
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "step3_词典.csv"),
                              index=False, encoding="utf-8-sig")
    print(f"词典规模: {len(rows)} 个词, 覆盖 {len(LEXICON)} 个维度")
    print("输出: output/step3_词典.csv, output/step3_tfidf_top20.csv")


if __name__ == "__main__":
    main()
