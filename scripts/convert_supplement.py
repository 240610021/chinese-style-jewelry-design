import os
import re
import markdown
from glob import glob

CSS = """
<style>
@page {
    size: A4;
    margin: 2.2cm 2cm 2.5cm 2cm;
    @top-center {
        content: string(doctitle);
        font-size: 8.5pt;
        color: #999;
        border-bottom: 0.5px solid #ddd;
        padding-bottom: 6px;
        font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    }
    @bottom-center {
        content: counter(page) " / " counter(pages);
        font-size: 8.5pt;
        color: #999;
        padding-top: 6px;
        border-top: 0.5px solid #ddd;
    }
}
@page :first {
    @top-center { content: none; }
    @bottom-center { content: none; }
}

body {
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
    font-size: 11pt;
    line-height: 1.85;
    color: #2c2c2c;
    max-width: 21cm;
    margin: 0 auto;
    padding: 0;
}

/* ===== 封面 ===== */
.cover {
    page-break-after: always;
    text-align: center;
    position: relative;
    height: 100vh;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 2cm;
}
.cover-band {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 1.4cm;
    background: linear-gradient(90deg, #7a0000 0%, #b32424 60%, #d44 100%);
}
.cover h1 {
    font-size: 30pt;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 0 0.6cm 0;
    padding: 0;
    border: none;
    line-height: 1.25;
    letter-spacing: 1px;
    string-set: doctitle content();
}
.cover .subtitle {
    font-size: 11pt;
    color: #555;
    line-height: 1.7;
    max-width: 85%;
    margin: 0 auto 1.5cm auto;
    padding: 0.5cm 0.8cm;
    background: #fafafa;
    border-left: 4px solid #b32424;
    border-right: 4px solid #b32424;
    text-align: justify;
}
.cover .meta {
    font-size: 10pt;
    color: #888;
    margin-top: 0.8cm;
}
.cover .deco-line {
    width: 3.5cm;
    height: 3px;
    background: linear-gradient(90deg, #7a0000, #b32424);
    margin: 1.2cm auto;
    border-radius: 2px;
}
.cover .tag {
    display: inline-block;
    font-size: 9pt;
    color: #b32424;
    border: 1px solid #b32424;
    padding: 3px 14px;
    border-radius: 20px;
    margin-top: 0.5cm;
    letter-spacing: 1px;
}

/* ===== 正文标题 ===== */
h1 {
    string-set: doctitle content();
    font-size: 20pt;
    color: #1a1a1a;
    text-align: center;
    margin-top: 0;
    margin-bottom: 0.7cm;
    padding-bottom: 0.35cm;
    border-bottom: 2.5px solid #7a0000;
    page-break-before: always;
}
h1:first-of-type { page-break-before: auto; }

h2 {
    font-size: 15pt;
    color: #1a1a1a;
    margin-top: 1cm;
    margin-bottom: 0.5cm;
    padding: 0.35cm 0.55cm;
    background: linear-gradient(90deg, #f5f5f5 0%, #fafafa 100%);
    border-left: 5px solid #7a0000;
    page-break-after: avoid;
    font-weight: 600;
}

h3 {
    font-size: 12.5pt;
    color: #333;
    margin-top: 0.7cm;
    margin-bottom: 0.35cm;
    padding-bottom: 0.15cm;
    border-bottom: 1.5px solid #e0e0e0;
    page-break-after: avoid;
    font-weight: 600;
}

h4 {
    font-size: 11.5pt;
    color: #444;
    margin-top: 0.5cm;
    margin-bottom: 0.25cm;
    font-weight: 600;
}

p { margin: 0.35cm 0; text-align: justify; }

/* ===== 表格 ===== */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 0.6cm 0;
    font-size: 10pt;
    page-break-inside: avoid;
    border-radius: 5px;
    overflow: hidden;
    border: 1px solid #d0d0d0;
}
th, td {
    padding: 8px 10px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid #e0e0e0;
    border-right: 1px solid #e0e0e0;
}
th:last-child, td:last-child { border-right: none; }
tr:last-child td { border-bottom: none; }

th {
    background-color: #7a0000;
    color: #fff;
    font-weight: 600;
    border-bottom: 2px solid #5a0000;
}
tr:nth-child(even) { background-color: #fafafa; }

/* ===== 代码块 ===== */
code {
    font-family: "SF Mono", "Courier New", monospace;
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9.5pt;
    color: #c7254e;
}
pre {
    background: #f8f8f8;
    padding: 0.5cm;
    border-radius: 5px;
    border-left: 4px solid #7a0000;
    overflow-x: auto;
    font-size: 9.5pt;
    line-height: 1.5;
    page-break-inside: avoid;
}
pre code {
    background: none;
    padding: 0;
    color: #333;
}

/* ===== 引用块 ===== */
blockquote {
    margin: 0.6cm 0;
    padding: 0.5cm 0.7cm;
    background: linear-gradient(90deg, #fafafa 0%, #f5f5f5 100%);
    border-left: 5px solid #b32424;
    color: #444;
    font-size: 10.5pt;
    line-height: 1.7;
    border-radius: 0 5px 5px 0;
}
blockquote p { margin: 0.2cm 0; }
blockquote p:first-child { margin-top: 0; }
blockquote p:last-child { margin-bottom: 0; }

/* ===== 列表 ===== */
ul, ol { margin: 0.4cm 0; padding-left: 1.2cm; }
li { margin: 0.15cm 0; }
ul li { list-style-type: disc; }
ul li li { list-style-type: circle; }

/* ===== 图片与分割线 ===== */
img { max-width: 100%; height: auto; display: block; margin: 0.5cm auto; }
hr { border: none; border-top: 1px solid #ddd; margin: 0.8cm 0; }

/* ===== 页脚注释 ===== */
.footer-note {
    text-align: center;
    font-size: 9pt;
    color: #999;
    margin-top: 2cm;
    padding-top: 0.4cm;
    border-top: 1px solid #e0e0e0;
}

/* ===== 流程/路径视觉增强 ===== */
blockquote strong {
    color: #7a0000;
}
</style>
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
{css}
</head>
<body>
<div class="cover">
    <div class="cover-band"></div>
    <h1>{title}</h1>
    {subtitle_html}
    <div class="deco-line"></div>
    <div class="meta">生成日期：2026年6月13日</div>
    <div class="tag">应聘补充资料</div>
</div>
{body}
<div class="footer-note">本文件仅供应聘展示使用 · 数据来源：公开市场信息及一手样本分析</div>
</body>
</html>
"""


def extract_subtitle(md_text):
    """提取 Markdown 中第一段 > 引用作为封面副标题"""
    lines = md_text.splitlines()
    subtitle_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('> '):
            subtitle_lines.append(stripped[2:])
        elif subtitle_lines:
            break
    if not subtitle_lines:
        return ''
    subtitle = ' '.join(subtitle_lines)
    # 去掉粗体标记，让纯文本更干净
    subtitle = re.sub(r'\*\*(.*?)\*\*', r'\1', subtitle)
    return f'<div class="subtitle">{subtitle}</div>'


def convert(md_path, out_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title = os.path.splitext(os.path.basename(md_path))[0]
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    subtitle_html = extract_subtitle(md_text)

    html = HTML_TEMPLATE.format(title=title, css=CSS, body=body_html, subtitle_html=subtitle_html)

    out_path = os.path.join(out_dir, title + '.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Converted: {title}")


def main():
    src_dir = r"g:\Downloads\蔡规划\应聘补充资料"
    out_dir = src_dir
    os.makedirs(out_dir, exist_ok=True)

    md_files = sorted(glob(os.path.join(src_dir, '*.md')))
    for md_path in md_files:
        convert(md_path, out_dir)

    print(f"\nDone. {len(md_files)} files converted to {out_dir}")


if __name__ == '__main__':
    main()
