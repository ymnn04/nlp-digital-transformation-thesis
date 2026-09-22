# -*- coding: utf-8 -*-
"""
Step 2 文本预处理
=================
流程：正则清洗 -> jieba 分词 -> 去停用词 -> 保留分词结果
输出：data/tokens.csv（每条语料一行，tokens 以空格连接）
"""
import os
import re
import jieba
import pandas as pd

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw_corpus.csv")
STOP = os.path.join(BASE, "code", "stopwords.txt")
OUT = os.path.join(BASE, "data", "tokens.csv")

_tokenizer = None


def get_stopwords():
    words = set()
    with open(STOP, encoding="utf-8") as f:
        for line in f:
            for w in line.split():
                if w:
                    words.add(w)
    return words


def clean_text(text):
    """清洗：去URL/乱码/多余空白，仅保留中英文、数字与常见符号"""
    text = re.sub(r"https?://\S+", " ", str(text))
    text = re.sub(r"[【】《》“”‘’…—※★●◆]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text, stopwords):
    global _tokenizer
    if _tokenizer is None:
        # 加入领域词，避免"数字化转型"等被切碎
        for w in ["数字化转型", "数字人民币", "数字孪生", "工业互联网", "人工智能",
                  "机器学习", "深度学习", "自然语言处理", "计算机视觉", "大数据",
                  "数据挖掘", "数据中台", "云计算", "边缘计算", "区块链",
                  "智能合约", "分布式账本", "智能制造", "电子商务", "互联网+",
                  "智慧物流", "智慧城市", "业财一体", "供应链"]:
            jieba.add_word(w)
        _tokenizer = jieba
    words = [w for w in _tokenizer.lcut(text)
             if w not in stopwords and len(w) > 1 and not re.match(r"^[\d\s\W]+$", w)]
    return words


def main():
    corpus = pd.read_csv(RAW)
    stopwords = get_stopwords()
    corpus["clean_text"] = corpus["mda_text"].map(clean_text)
    corpus["tokens"] = corpus["clean_text"].map(lambda t: " ".join(tokenize(t, stopwords)))
    corpus["n_tokens"] = corpus["tokens"].str.split().str.len()
    corpus.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"分词完成：平均每条 {corpus['n_tokens'].mean():.0f} 词")
    print("输出: data/tokens.csv")


if __name__ == "__main__":
    main()
