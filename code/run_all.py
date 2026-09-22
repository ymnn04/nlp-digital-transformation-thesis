# -*- coding: utf-8 -*-
"""
一键复现：按顺序执行五步流水线
用法: python run_all.py
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    "step0_make_demo_corpus.py",
    "step1_acquire.py",
    "step2_preprocess.py",
    "step3_lexicon.py",
    "step4_measure.py",
    "step5_validity_regression.py",
]

for s in STEPS:
    print("=" * 60)
    print(">>> 运行", s)
    r = subprocess.run([sys.executable, os.path.join(HERE, s)])
    if r.returncode != 0:
        sys.exit(f"[失败] {s} 退出码 {r.returncode}")
print("=" * 60)
print("五步流水线全部完成。结果见 data/ 与 output/ 目录。")
