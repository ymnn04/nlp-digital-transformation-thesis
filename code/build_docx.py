"""从 final_draft.md 构建毕业论文模拟稿 DOCX。
- 封面页 / 摘要 / 关键信息说明 / 目录域 / 正文（一~四级标题）
- 三线表 / 插图（按"图N"就近插入）/ 公式居中 / GB/T 7714 参考文献
"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = r"C:\Users\杨淼\WorkBuddy\2026-09-21-19-07-07"
MD = rf"{ROOT}\output\20260921-nlp-thesis-mock\stage1\final_draft.md"
IMG_DIR = rf"{ROOT}\output\20260921-nlp-thesis-mock\stage2\images"
OUT = rf"{ROOT}\nlp-measure-thesis\paper\数字化转型测度模拟论文.docx"

IMG_MAP = {
    1: ("fig1_年度趋势.png", "图1　企业数字化转型测度的年度趋势（分行业）"),
    2: ("fig2_测度分布.png", "图2　数字化转型测度的分布"),
    3: ("fig3_维度相关.png", "图3　五维度词频相关矩阵（效度佐证）"),
    4: ("fig4_分组比较.png", "图4　不同数字化水平的ROA分组比较（演示数据）"),
}

# ---------- 基础样式 ----------
doc = Document()
sec = doc.sections[0]
sec.page_height = Cm(29.7)
sec.page_width = Cm(21.0)
sec.top_margin = Cm(3.0)
sec.bottom_margin = Cm(2.5)
sec.left_margin = Cm(3.0)
sec.right_margin = Cm(2.5)


def set_cjk(run, font="宋体"):
    run.font.name = font
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:eastAsia"), font)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)


normal = doc.styles["Normal"]
normal.font.size = Pt(12)
normal.font.name = "宋体"
normal._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "宋体")
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.first_line_indent = Pt(24)

for h, sz in (("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 12)):
    st = doc.styles[h]
    st.font.size = Pt(sz)
    st.font.bold = True
    st.font.name = "黑体"
    st._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "黑体")
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.first_line_indent = Pt(0)
    st.paragraph_format.space_before = Pt(6)
    st.paragraph_format.space_after = Pt(6)


def add_runs(par, text, bold_default=False):
    """解析 **加粗** 片段写入段落。"""
    parts = re.split(r"(\*\*.*?\*\*)", text)
    for p in parts:
        if not p:
            continue
        if p.startswith("**") and p.endswith("**"):
            r = par.add_run(p[2:-2])
            r.bold = True
        else:
            r = par.add_run(p)
            r.bold = bold_default
        set_cjk(r)


def para(text="", style=None, align=None, size=None, bold=False, italic=False,
         indent=True, color_block=False):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    if size or bold or italic or color_block:
        if text:
            r = p.add_run(text)
            if size:
                r.font.size = Pt(size)
            r.bold = bold
            r.italic = italic
            if color_block:
                r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            set_cjk(r)
    elif text:
        add_runs(p, text)
    if indent and style is None:
        p.paragraph_format.first_line_indent = Pt(24)
    else:
        p.paragraph_format.first_line_indent = Pt(0)
    return p


def set_cell_borders(cell, edges):
    tcPr = cell._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcPr.append(b)
    for edge, (val, sz) in edges.items():
        el = b.find(qn("w:" + edge))
        if el is None:
            el = OxmlElement("w:" + edge)
            b.append(el)
        el.set(qn("w:val"), val)
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")


def three_line_table(rows):
    n = len(rows)
    t = doc.add_table(rows=n, cols=len(rows[0]))
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Pt(0)
            r = p.add_run(str(val))
            set_cjk(r)
            r.font.size = Pt(10.5)
            if i == 0:
                r.bold = True
    # 三线：表头上行双线、表头下行单线、末行底线双线；无竖线
    for i in range(n):
        for j in range(len(rows[0])):
            cell = t.cell(i, j)
            if i == 0:
                set_cell_borders(cell, {"top": ("double", 18), "bottom": ("single", 8)})
            elif i == n - 1:
                set_cell_borders(cell, {"bottom": ("double", 18)})
            else:
                set_cell_borders(cell, {})
    return t


def add_image(fig_no):
    fn, cap = IMG_MAP[fig_no]
    path = rf"{IMG_DIR}\{fn}"
    import os
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        p.add_run().add_picture(path, width=Cm(12.5))
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.first_line_indent = Pt(0)
        r = cp.add_run(cap)
        r.font.size = Pt(10.5)
        set_cjk(r)


def add_toc_field():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("目录")
    r.bold = True
    r.font.size = Pt(15)
    set_cjk(r)
    p.paragraph_format.first_line_indent = Pt(0)
    fld = doc.add_paragraph()
    fld.paragraph_format.first_line_indent = Pt(0)
    run = fld.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = "（在 Word 中右键“更新域”以生成目录）"
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instr)
    run._r.append(fldChar2)
    run._r.append(t)
    run._r.append(fldChar3)


# ---------- 解析 Markdown ----------
lines = open(MD, encoding="utf-8").read().splitlines()
inserted_figs = set()

i = 0
n = len(lines)
while i < n:
    line = lines[i].rstrip()

    # 封面标题（# 标题）
    if line.startswith("# ") and i == 0:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        r = p.add_run(line[2:])
        r.bold = True
        r.font.size = Pt(18)
        set_cjk(r)
        i += 1
        continue

    # 作者行（**作者：...**）
    if line.startswith("**作者"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        m = re.match(r"\*\*(.*)\*\*", line)
        r = p.add_run(m.group(1) if m else line)
        r.font.size = Pt(11)
        set_cjk(r)
        i += 1
        continue

    # 说明框（**说明：...**）
    if line.startswith("**说明"):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        m = re.match(r"\*\*(.*)\*\*", line)
        r = p.add_run(m.group(1) if m else line)
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        set_cjk(r)
        i += 1
        continue

    # 一级标题 ##
    if line.startswith("## "):
        doc.add_page_break() if line[3:].strip() == "参考文献" else None
        p = doc.add_paragraph(line[3:], style="Heading 1")
        i += 1
        continue

    # 二级标题 ###
    if line.startswith("### "):
        doc.add_paragraph(line[4:], style="Heading 2")
        i += 1
        continue

    # 表格（连续 | 行）
    if line.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:\-\|]+\|\s*$", lines[i + 1]):
        # 收集表头+数据，跳过分隔行
        tbl = []
        j = i
        while j < n and lines[j].lstrip().startswith("|"):
            if re.match(r"^\s*\|[\s:\-\|]+\|\s*$", lines[j]):
                j += 1
                continue
            cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
            tbl.append(cells)
            j += 1
        if len(tbl) >= 2:
            three_line_table(tbl)
        i = j
        continue

    # 表标题粗体行（**表X-X ...**）
    if re.match(r"^\*\*表", line):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        m = re.match(r"\*\*(.*)\*\*", line)
        r = p.add_run(m.group(1) if m else line)
        r.bold = True
        r.font.size = Pt(10.5)
        set_cjk(r)
        i += 1
        continue

    # 注释行（以"注："开头）
    if line.startswith("注："):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        r = p.add_run(line)
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        set_cjk(r)
        i += 1
        continue

    # 空行
    if line.strip() == "":
        i += 1
        continue

    # 公式行（含 = 与下标 _it / 希腊字母，且较短）
    if ("=" in line) and ("_it" in line or "α" in line or "β" in line) and len(line) < 140:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0)
        r = p.add_run(line)
        r.italic = True
        r.font.size = Pt(12)
        set_cjk(r)
        i += 1
        continue

    # 普通正文：写入后，若含 图N 则就近插图
    p = para(line)
    for k in range(1, 5):
        if f"图{k}" in line and k not in inserted_figs and k in IMG_MAP:
            inserted_figs.add(k)
            add_image(k)
    i += 1

doc.save(OUT)
print("DOCX 已生成:", OUT)
import os
print("大小(bytes):", os.path.getsize(OUT))
print("已插图:", sorted(inserted_figs))
