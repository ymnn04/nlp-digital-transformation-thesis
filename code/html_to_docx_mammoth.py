"""将格式化后的论文 HTML 转换为 Word (.docx)。
使用 mammoth：保留标题层级、加粗、表格、列表、图片。
图片通过 convert_image 从本地 images 目录嵌入。
"""
import os
import mammoth

HTML = r"C:\Users\杨淼\WorkBuddy\2026-09-21-19-07-07\output\20260921-nlp-thesis-mock\stage2\formatted-数字化转型测度模拟论文.html"
IMG_DIR = r"C:\Users\杨淼\WorkBuddy\2026-09-21-19-07-07\output\20260921-nlp-thesis-mock\stage2\images"
OUT = r"C:\Users\杨淼\WorkBuddy\2026-09-21-19-07-07\nlp-measure-thesis\paper\数字化转型测度模拟论文.docx"

style_map = """
p[style-name='Heading 1'] => h1:fresh
p[style-name='Heading 2'] => h2:fresh
p[style-name='Heading 3'] => h3:fresh
p[style-name='Title'] => h1:fresh
table => table:fresh
"""

def convert_image(image):
    with image.open() as f:
        # 从 HTML 的 src 取出文件名，定位本地图片
        src = image.alt_text or ""
        name = os.path.basename(src) if src else None
        path = os.path.join(IMG_DIR, name) if name else None
        if path and os.path.exists(path):
            with open(path, "rb") as imgf:
                data = imgf.read()
            return {
                "src": path,
                "content_type": "image/png",
                "data": data,
            }
        # 退回：使用 mammoth 默认（尝试按 src 路径）
        return mammoth.images.inline(image)

with open(HTML, "r", encoding="utf-8") as f:
    result = mammoth.convert(
        f,
        style_map=style_map,
        convert_image=mammoth.images.img_element(convert_image),
    )

with open(OUT, "wb") as f:
    f.write(result.value)

print("DOCX 已写出:", OUT)
print("messages:", result.messages[:10] if result.messages else "无")
import os as _os
print("文件大小(bytes):", _os.path.getsize(OUT))
