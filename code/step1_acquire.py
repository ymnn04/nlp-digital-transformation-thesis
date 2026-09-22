# -*- coding: utf-8 -*-
"""
Step 1 文本获取与语料登记
=========================
真实数据获取路径（论文"数据来源"部分需写明）：
1. 登录巨潮资讯网 http://www.cninfo.com.cn ，按股票代码与年份检索"年度报告"；
2. 下载年报全文（PDF/HTML），用 pdfplumber / pdfminer 提取文本，或使用
   CNRDS、文数、WinGo 等学术文本数据库直接获取年报MD&A文本；
3. 截取"管理层讨论与分析"(MD&A)章节，汇总为 csv：每行一条
   [stock_code, firm_name, industry, year, mda_text]。

本脚本负责读取语料表并输出获取登记表（语料清单+字数统计），
演示模式下读取 step0 生成的 data/raw_corpus.csv。
"""
import os
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw_corpus.csv")
OUT = os.path.join(BASE, "output")
os.makedirs(OUT, exist_ok=True)


def main():
    corpus = pd.read_csv(RAW)
    # 基础质检：关键字段是否缺失、文本是否过短
    corpus["text_len"] = corpus["mda_text"].astype(str).str.len()
    bad = corpus[corpus["text_len"] < 50]
    if len(bad):
        print(f"[警告] {len(bad)} 条文本长度<50字符，建议核查")

    log = corpus[["stock_code", "firm_name", "industry", "year",
                  "report_type", "text_len", "source_note"]]
    log.to_csv(os.path.join(OUT, "step1_获取登记表.csv"),
               index=False, encoding="utf-8-sig")
    print(f"语料 {len(corpus)} 条，平均文本长度 {corpus['text_len'].mean():.0f} 字符")
    print("输出: output/step1_获取登记表.csv")


if __name__ == "__main__":
    main()
