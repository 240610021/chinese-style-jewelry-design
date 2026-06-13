import os
import markdown
from glob import glob

CSS = """
<style>
@page { size: A4; margin: 2cm; }
@page :first { @top-center { content: none; } @bottom-center { content: none; } }

body {
    font-family: "PingFang SC", "Microsoft YaHei", "SimSun", sans-serif;
    font-size: 11pt;
    line-height: 1.8;
    color: #222;
    max-width: 21cm;
    margin: 0 auto;
    padding: 2cm;
}

h1 {
    font-size: 22pt;
    text-align: center;
    border-bottom: 3px double #333;
    padding-bottom: 0.5cm;
    margin-top: 0;
    margin-bottom: 1cm;
    page-break-before: always;
}

h1:first-of-type { page-break-before: auto; }

h2 {
    font-size: 16pt;
    color: #1a1a1a;
    border-left: 5px solid #c00;
    padding-left: 0.4cm;
    margin-top: 1.2cm;
    margin-bottom: 0.6cm;
    page-break-after: avoid;
}

h3 {
    font-size: 13pt;
    color: #333;
    margin-top: 0.8cm;
    margin-bottom: 0.4cm;
    page-break-after: avoid;
}

h4 {
    font-size: 12pt;
    color: #444;
    margin-top: 0.6cm;
    margin-bottom: 0.3cm;
}

p {
    margin: 0.4cm 0;
    text-align: justify;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 0.6cm 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #666;
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
}

th {
    background-color: #f2f2f2;
    font-weight: bold;
}

tr:nth-child(even) { background-color: #fafafa; }

code {
    font-family: "Courier New", monospace;
    background: #f5f5f5;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 10pt;
}

pre {
    background: #f5f5f5;
    padding: 0.5cm;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 9.5pt;
    line-height: 1.5;
    page-break-inside: avoid;
}

blockquote {
    border-left: 4px solid #c00;
    margin: 0.6cm 0;
    padding: 0.3cm 0.6cm;
    background: #fafafa;
    color: #444;
}

ul, ol {
    margin: 0.4cm 0;
    padding-left: 1.2cm;
}

li {
    margin: 0.15cm 0;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 0.5cm auto;
}

hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 1cm 0;
}

.cover {
    text-align: center;
    padding-top: 6cm;
    page-break-after: always;
}

.cover h1 {
    border: none;
    font-size: 28pt;
    margin-bottom: 1cm;
}

.cover .subtitle {
    font-size: 14pt;
    color: #666;
    margin-top: 0.5cm;
}

.footer-note {
    text-align: center;
    font-size: 9pt;
    color: #888;
    margin-top: 2cm;
    border-top: 1px solid #ddd;
    padding-top: 0.3cm;
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
<h1>{title}</h1>
<div class="subtitle">中高端国潮银饰（错铜工艺）应聘补充资料</div>
<div class="subtitle" style="margin-top:2cm;">生成日期：2026年6月13日</div>
</div>
{body}
<div class="footer-note">本文件仅供应聘展示使用 · 数据来源：公开市场信息及一手样本分析</div>
</body>
</html>
"""


def convert(md_path, out_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title = os.path.splitext(os.path.basename(md_path))[0]
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])

    html = HTML_TEMPLATE.format(title=title, css=CSS, body=body_html)

    out_path = os.path.join(out_dir, title + '.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Converted: {title}")


def main():
    src_dir = r"g:\Downloads\蔡规划\应聘补充资料"
    out_dir = src_dir
    os.makedirs(out_dir, exist_ok=True)

    md_files = glob(os.path.join(src_dir, '*.md'))
    for md_path in md_files:
        convert(md_path, out_dir)

    print(f"\nDone. {len(md_files)} files converted to {out_dir}")


if __name__ == '__main__':
    main()
