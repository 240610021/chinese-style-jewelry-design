import re

html_path = r"g:\Downloads\蔡规划\应聘补充资料\01_中高端国潮错铜银饰赛道可行性研究.html"
out_path = r"g:\Downloads\蔡规划\应聘补充资料\01_中高端国潮错铜银饰赛道可行性研究.html"

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 subtitle
subtitle_m = re.search(r'<div class="subtitle">(.*?)</div>', content, re.DOTALL)
subtitle = subtitle_m.group(1) if subtitle_m else ''

# 提取 body 内的正文内容（从第一个带 id 的 h1 开始到 footer-note 之前）
body_m = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
full_body = body_m.group(1)

# 找到正文开始位置（第一个 <h1 id=）
h1_start = full_body.find('<h1 id=')
# 找到 footer 开始位置
footer_start = full_body.rfind('<div class="footer-note">')
main_content = full_body[h1_start:footer_start].strip()

title = "中高端国潮错铜银饰赛道可行性研究"

new_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
@page {{
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @top-center {{ content: string(doctitle); font-size: 8pt; color: #aaa; font-family: "PingFang SC", "Microsoft YaHei", sans-serif; }}
    @bottom-center {{ content: counter(page); font-size: 8pt; color: #aaa; }}
}}
@page :first {{ @top-center {{ content: none; }} @bottom-center {{ content: none; }} }}

body {{
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans SC", sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #333;
    max-width: 21cm;
    margin: 0 auto;
    padding: 0;
}}

/* ===== 封面：对角线分割 + 几何装饰 ===== */
.cover {{
    page-break-after: always;
    position: relative;
    height: 100vh;
    overflow: hidden;
    box-sizing: border-box;
    padding: 0;
}}
.cover::before {{
    content: '';
    position: absolute;
    top: -30%;
    left: -20%;
    width: 90%;
    height: 120%;
    background: linear-gradient(135deg, #8B0000 0%, #c41e3a 60%, #d44 100%);
    transform: rotate(-15deg);
    z-index: 0;
}}
.cover::after {{
    content: '';
    position: absolute;
    bottom: 10%;
    right: 5%;
    width: 180px;
    height: 180px;
    border: 4px solid rgba(212, 160, 23, 0.4);
    border-radius: 50%;
    z-index: 1;
}}
.cover-deco-circle {{
    position: absolute;
    top: 15%;
    right: 15%;
    width: 80px;
    height: 80px;
    background: rgba(212, 160, 23, 0.15);
    border-radius: 50%;
    z-index: 1;
}}
.cover-content {{
    position: relative;
    z-index: 2;
    padding: 3cm 2.5cm;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}}
.cover-tag {{
    display: inline-block;
    background: rgba(255,255,255,0.15);
    color: #fff;
    font-size: 9pt;
    padding: 4px 16px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.3);
    margin-bottom: 1.5cm;
    letter-spacing: 2px;
    width: fit-content;
}}
.cover h1 {{
    font-size: 34pt;
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.8cm 0;
    line-height: 1.2;
    letter-spacing: 2px;
    string-set: doctitle content();
    text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}}
.cover-subtitle {{
    font-size: 11pt;
    color: rgba(255,255,255,0.9);
    line-height: 1.7;
    max-width: 55%;
    text-align: justify;
}}
.cover-meta {{
    position: absolute;
    bottom: 2cm;
    left: 2.5cm;
    font-size: 9pt;
    color: rgba(255,255,255,0.7);
}}
.cover-accent {{
    position: absolute;
    bottom: 2cm;
    right: 2.5cm;
    width: 60px;
    height: 4px;
    background: #d4a017;
    border-radius: 2px;
}}

/* ===== 正文标题 ===== */
h1 {{
    string-set: doctitle content();
    font-size: 18pt;
    color: #1a1a1a;
    text-align: center;
    margin-top: 0;
    margin-bottom: 0.6cm;
    padding-bottom: 0.3cm;
    border-bottom: 3px solid #c41e3a;
    page-break-before: always;
}}
h1:first-of-type {{ page-break-before: auto; }}

h2 {{
    font-size: 14pt;
    color: #1a1a1a;
    margin-top: 0.9cm;
    margin-bottom: 0.5cm;
    padding: 0.3cm 0;
    page-break-after: avoid;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.4cm;
}}
h2::before {{
    content: '';
    display: inline-block;
    width: 6px;
    height: 18px;
    background: linear-gradient(180deg, #c41e3a, #d4a017);
    border-radius: 3px;
    flex-shrink: 0;
}}

h3 {{
    font-size: 12pt;
    color: #c41e3a;
    margin-top: 0.6cm;
    margin-bottom: 0.3cm;
    padding-left: 0.4cm;
    border-left: 3px solid #d4a017;
    page-break-after: avoid;
    font-weight: 600;
}}

h4 {{
    font-size: 11pt;
    color: #444;
    margin-top: 0.4cm;
    margin-bottom: 0.2cm;
    font-weight: 600;
}}

p {{ margin: 0.3cm 0; text-align: justify; }}

/* ===== 表格 ===== */
table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 0.5cm 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #e8e8e8;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}}
.table-topbar {{
    height: 4px;
    background: linear-gradient(90deg, #c41e3a, #d4a017);
    border-radius: 6px 6px 0 0;
}}
th, td {{
    padding: 7px 9px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid #eee;
}}
th {{
    background-color: #fafafa;
    color: #8B0000;
    font-weight: 700;
    font-size: 9pt;
    border-bottom: 2px solid #c41e3a;
}}
tr:nth-child(even) {{ background-color: #fdfdfd; }}
tr:last-child td {{ border-bottom: none; }}

/* ===== 代码块 ===== */
code {{
    font-family: "SF Mono", monospace;
    background: #fff5f5;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 9pt;
    color: #c41e3a;
}}
pre {{
    background: #fafafa;
    padding: 0.5cm;
    border-radius: 6px;
    border-left: 4px solid #d4a017;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
    page-break-inside: avoid;
}}

/* ===== 引用块：大引号装饰 ===== */
blockquote {{
    margin: 0.5cm 0;
    padding: 0.6cm 0.8cm 0.6cm 1.2cm;
    background: linear-gradient(135deg, #fff9f9 0%, #fff 100%);
    border-left: 4px solid #c41e3a;
    color: #555;
    font-size: 10.5pt;
    line-height: 1.7;
    border-radius: 0 8px 8px 0;
    position: relative;
}}
blockquote::before {{
    content: '“';
    position: absolute;
    top: 0.2cm;
    left: 0.3cm;
    font-size: 24pt;
    color: #c41e3a;
    opacity: 0.3;
    font-family: Georgia, serif;
    line-height: 1;
}}
blockquote p {{ margin: 0.15cm 0; }}

/* ===== 列表：自定义标记 ===== */
ul, ol {{ margin: 0.3cm 0; padding-left: 1cm; }}
li {{ margin: 0.12cm 0; }}
ul li {{ list-style: none; position: relative; padding-left: 0.5cm; }}
ul li::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 0.5em;
    width: 6px;
    height: 6px;
    background: linear-gradient(135deg, #c41e3a, #d4a017);
    border-radius: 50%;
    transform: translateY(-50%);
}}
ul li li::before {{
    width: 5px;
    height: 5px;
    background: #d4a017;
    border-radius: 0;
    transform: translateY(-50%) rotate(45deg);
}}

/* ===== 图片与分割线 ===== */
img {{ max-width: 100%; height: auto; display: block; margin: 0.5cm auto; }}
hr {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #c41e3a, #d4a017, transparent);
    margin: 0.8cm 0;
    border-radius: 1px;
}}

/* ===== 页脚注释 ===== */
.footer-note {{
    text-align: center;
    font-size: 8.5pt;
    color: #aaa;
    margin-top: 1.5cm;
    padding-top: 0.3cm;
    border-top: 1px solid #eee;
}}
</style>
</head>
<body>
<div class="cover">
    <div class="cover-deco-circle"></div>
    <div class="cover-content">
        <div class="cover-tag">应聘补充资料</div>
        <h1>{title}</h1>
        <div class="cover-subtitle">{subtitle}</div>
    </div>
    <div class="cover-meta">生成日期：2026年6月13日</div>
    <div class="cover-accent"></div>
</div>
{main_content}
<div class="footer-note">本文件仅供应聘展示使用 · 数据来源：公开市场信息及一手样本分析</div>
</body>
</html>
'''

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Done: sample redesign written.")
