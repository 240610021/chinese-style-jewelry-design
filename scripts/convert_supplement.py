import os
import re
import markdown
from glob import glob

CSS = """
<style>
@page {
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @top-center { content: string(doctitle); font-size: 8pt; color: #aaa; font-family: "PingFang SC", sans-serif; }
    @bottom-center { content: counter(page); font-size: 8pt; color: #aaa; }
}
@page :first { @top-center { content: none; } @bottom-center { content: none; } }

body {
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #333;
    max-width: 21cm;
    margin: 0 auto;
    padding: 0;
}

/* ===== 封面 ===== */
.cover {
    page-break-after: always;
    position: relative;
    height: 100vh;
    overflow: hidden;
    box-sizing: border-box;
    padding: 0;
}
.cover::before {
    content: '';
    position: absolute;
    top: -30%;
    left: -20%;
    width: 90%;
    height: 120%;
    background: linear-gradient(135deg, #8B0000 0%, #c41e3a 60%, #d44 100%);
    transform: rotate(-15deg);
    z-index: 0;
}
.cover::after {
    content: '';
    position: absolute;
    bottom: 10%;
    right: 5%;
    width: 180px;
    height: 180px;
    border: 4px solid rgba(212,160,23,0.4);
    border-radius: 50%;
    z-index: 1;
}
.cover-deco-circle {
    position: absolute;
    top: 15%;
    right: 15%;
    width: 80px;
    height: 80px;
    background: rgba(212,160,23,0.15);
    border-radius: 50%;
    z-index: 1;
}
.cover-content {
    position: relative;
    z-index: 2;
    padding: 3cm 2.5cm;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.cover-tag {
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
}
.cover h1 {
    font-size: 34pt;
    font-weight: 700;
    color: #fff;
    margin: 0 0 0.8cm 0;
    line-height: 1.2;
    letter-spacing: 2px;
    string-set: doctitle content();
    text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}
.cover-subtitle {
    font-size: 11pt;
    color: rgba(255,255,255,0.9);
    line-height: 1.7;
    max-width: 55%;
    text-align: justify;
}
.cover-meta {
    position: absolute;
    bottom: 2cm;
    left: 2.5cm;
    font-size: 9pt;
    color: rgba(255,255,255,0.7);
}
.cover-accent {
    position: absolute;
    bottom: 2cm;
    right: 2.5cm;
    width: 60px;
    height: 4px;
    background: #d4a017;
    border-radius: 2px;
}

/* ===== 正文标题 ===== */
h1 {
    string-set: doctitle content();
    font-size: 18pt;
    color: #1a1a1a;
    text-align: center;
    margin-top: 0;
    margin-bottom: 0.6cm;
    padding-bottom: 0.3cm;
    border-bottom: 3px solid #c41e3a;
    page-break-before: always;
}
h1:first-of-type { page-break-before: auto; }

h2 {
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
}
h2::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 18px;
    background: linear-gradient(180deg, #c41e3a, #d4a017);
    border-radius: 3px;
    flex-shrink: 0;
}
h3 {
    font-size: 12pt;
    color: #c41e3a;
    margin-top: 0.6cm;
    margin-bottom: 0.3cm;
    padding-left: 0.4cm;
    border-left: 3px solid #d4a017;
    page-break-after: avoid;
    font-weight: 600;
}
h4 {
    font-size: 11pt;
    color: #444;
    margin-top: 0.4cm;
    margin-bottom: 0.2cm;
    font-weight: 600;
}
p { margin: 0.3cm 0; text-align: justify; }

/* ===== 表格 ===== */
table {
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
}
th, td {
    padding: 7px 9px;
    text-align: left;
    vertical-align: top;
    border-bottom: 1px solid #eee;
}
th {
    background-color: #fafafa;
    color: #8B0000;
    font-weight: 700;
    font-size: 9pt;
    border-bottom: 2px solid #c41e3a;
}
tr:nth-child(even) { background-color: #fdfdfd; }
tr:last-child td { border-bottom: none; }

/* ===== 代码 ===== */
code {
    font-family: "SF Mono", monospace;
    background: #fff5f5;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 9pt;
    color: #c41e3a;
}
pre {
    background: #fafafa;
    padding: 0.5cm;
    border-radius: 6px;
    border-left: 4px solid #d4a017;
    overflow-x: auto;
    font-size: 9pt;
    line-height: 1.5;
    page-break-inside: avoid;
}

/* ===== 引用块 ===== */
blockquote {
    margin: 0.5cm 0;
    padding: 0.6cm 0.8cm 0.6cm 1.2cm;
    background: linear-gradient(135deg, #fff9f9 0%, #fff 100%);
    border-left: 4px solid #c41e3a;
    color: #555;
    font-size: 10.5pt;
    line-height: 1.7;
    border-radius: 0 8px 8px 0;
    position: relative;
}
blockquote::before {
    content: '“';
    position: absolute;
    top: 0.2cm;
    left: 0.3cm;
    font-size: 24pt;
    color: #c41e3a;
    opacity: 0.3;
    font-family: Georgia, serif;
    line-height: 1;
}
blockquote p { margin: 0.15cm 0; }

/* ===== 列表 ===== */
ul, ol { margin: 0.3cm 0; padding-left: 1cm; }
li { margin: 0.12cm 0; }
ul li { list-style: none; position: relative; padding-left: 0.5cm; }
ul li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.5em;
    width: 6px;
    height: 6px;
    background: linear-gradient(135deg, #c41e3a, #d4a017);
    border-radius: 50%;
    transform: translateY(-50%);
}
ul li li::before {
    width: 5px;
    height: 5px;
    background: #d4a017;
    border-radius: 0;
    transform: translateY(-50%) rotate(45deg);
}

/* ===== 分割线 ===== */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #c41e3a, #d4a017, transparent);
    margin: 0.8cm 0;
    border-radius: 1px;
}

/* ===== 可视化：仪表盘 ===== */
.dashboard {
    display: flex;
    gap: 0.4cm;
    margin: 0.5cm 0 0.8cm 0;
    page-break-inside: avoid;
}
.dash-card {
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 3px solid #c41e3a;
    border-radius: 6px;
    padding: 0.4cm;
    text-align: center;
}
.dash-num {
    font-size: 18pt;
    font-weight: 700;
    color: #c41e3a;
    line-height: 1.1;
}
.dash-label {
    font-size: 8.5pt;
    color: #888;
    margin-top: 0.15cm;
}
.dash-trend {
    font-size: 8pt;
    margin-top: 0.1cm;
}
.dash-trend.up { color: #c41e3a; }
.dash-trend.down { color: #888; }

/* ===== 可视化：堆叠条形图 ===== */
.viz-title {
    font-size: 10pt;
    font-weight: 700;
    color: #8B0000;
    margin: 0.6cm 0 0.3cm 0;
    padding-left: 0.3cm;
    border-left: 3px solid #d4a017;
}
.bar-compare {
    margin: 0.3cm 0;
    page-break-inside: avoid;
}
.bar-row {
    display: flex;
    align-items: center;
    gap: 0.3cm;
    margin: 0.25cm 0;
}
.bar-label {
    font-size: 9pt;
    color: #555;
    width: 4.5em;
    text-align: right;
    flex-shrink: 0;
}
.bar-track {
    flex: 1;
    height: 18px;
    background: #f0f0f0;
    border-radius: 9px;
    overflow: hidden;
    display: flex;
}
.bar-seg {
    height: 100%;
}
.bar-seg.silver { background: linear-gradient(90deg, #c41e3a, #e44); }
.bar-seg.copper { background: linear-gradient(90deg, #d4a017, #e6c35c); }
.bar-seg.labor { background: linear-gradient(90deg, #666, #999); }
.bar-pct {
    font-size: 8pt;
    color: #888;
    width: 7em;
    flex-shrink: 0;
}
.bar-legend {
    display: flex;
    gap: 0.5cm;
    justify-content: center;
    margin-top: 0.2cm;
    font-size: 8pt;
    color: #666;
}
.leg-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    margin-right: 3px;
    vertical-align: middle;
}
.leg-dot.silver { background: linear-gradient(135deg, #c41e3a, #e44); }
.leg-dot.copper { background: linear-gradient(135deg, #d4a017, #e6c35c); }
.leg-dot.labor { background: linear-gradient(135deg, #666, #999); }

/* ===== 可视化：威胁度条形图 ===== */
.threat-chart {
    margin: 0.3cm 0;
    page-break-inside: avoid;
}
.t-row {
    display: flex;
    align-items: center;
    gap: 0.3cm;
    margin: 0.2cm 0;
}
.t-name {
    font-size: 9pt;
    color: #555;
    width: 5em;
    text-align: right;
    flex-shrink: 0;
}
.t-track {
    flex: 1;
    height: 14px;
    background: #f0f0f0;
    border-radius: 7px;
    overflow: hidden;
}
.t-bar {
    height: 100%;
    border-radius: 7px;
}
.t-bar.t5 { background: linear-gradient(90deg, #8B0000, #c41e3a); width: 100%; }
.t-bar.t3 { background: linear-gradient(90deg, #c41e3a, #e66); }
.t-bar.t2 { background: linear-gradient(90deg, #e66, #f88); }
.t-pct {
    font-size: 8pt;
    color: #888;
    width: 3em;
    flex-shrink: 0;
}

/* ===== 可视化：环形图/饼图 ===== */
.donut-wrap, .pie-wrap {
    display: flex;
    align-items: center;
    gap: 0.8cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}
.donut, .pie {
    width: 220px;
    height: 220px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: inset 0 0 0 36px #fff;
}
.donut-legend, .pie-legend {
    flex: 1;
}
.d-leg, .p-leg {
    font-size: 9pt;
    color: #555;
    margin: 0.15cm 0;
    display: flex;
    align-items: center;
    gap: 0.2cm;
}
.d-dot, .p-dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
}

/* ===== 可视化：GMV柱状图 ===== */
.gmv-chart {
    display: flex;
    align-items: flex-end;
    gap: 0.4cm;
    height: 120px;
    margin: 0.4cm 0;
    padding: 0.3cm 0.5cm;
    background: #fafafa;
    border-radius: 6px;
    page-break-inside: avoid;
}
.g-col {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
}
.g-bar {
    width: 60%;
    background: linear-gradient(180deg, #c41e3a, #8B0000);
    border-radius: 4px 4px 0 0;
    min-height: 8px;
}
.g-label {
    font-size: 8pt;
    color: #888;
    margin-top: 0.15cm;
}
.g-val {
    font-size: 9pt;
    font-weight: 700;
    color: #c41e3a;
    margin-top: 0.05cm;
}
.gmv-total {
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-top: 0.3cm;
}
.gmv-total strong {
    color: #c41e3a;
    font-size: 12pt;
}

/* ===== 可视化：产品矩阵三列卡片 ===== */
.matrix-three {
    display: flex;
    gap: 0.4cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}
.m-card {
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 4px solid #d4a017;
    border-radius: 6px;
    padding: 0.4cm;
    text-align: center;
}
.m-card.m-main { border-top-color: #c41e3a; background: linear-gradient(135deg, #fff5f5, #fff); }
.m-card.m-lux { border-top-color: #8B0000; background: linear-gradient(135deg, #f8f0f0, #fff); }
.m-tier {
    font-size: 8pt;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.2cm;
}
.m-name {
    font-size: 14pt;
    font-weight: 700;
    color: #1a1a1a;
}
.m-price {
    font-size: 10pt;
    color: #c41e3a;
    font-weight: 600;
    margin: 0.15cm 0;
}
.m-scene {
    font-size: 8.5pt;
    color: #888;
}

/* ===== 通用卡片行 ===== */
.card-row {
    display: flex;
    gap: 0.4cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}
.g-card {
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 3px solid #c41e3a;
    border-radius: 6px;
    padding: 0.4cm;
    text-align: center;
}
.g-card.g2 { border-top-color: #d4a017; }
.g-card.g3 { border-top-color: #8B0000; }
.g-card.g4 { border-top-color: #666; }
.g-card.g5 { border-top-color: #e66; }
.g-title {
    font-size: 10pt;
    font-weight: 700;
    color: #1a1a1a;
    margin-bottom: 0.15cm;
}
.g-desc {
    font-size: 8.5pt;
    color: #888;
}
.g-num {
    font-size: 14pt;
    font-weight: 700;
    color: #c41e3a;
    margin: 0.1cm 0;
}

/* ===== 时间轴 ===== */
.timeline {
    display: flex;
    gap: 0.3cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}
.tl-item {
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 3px solid #c41e3a;
    border-radius: 6px;
    padding: 0.35cm;
    text-align: center;
    position: relative;
}
.tl-item::after {
    content: '';
    position: absolute;
    top: 50%;
    right: -0.35cm;
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-left: 6px solid #c41e3a;
    transform: translateY(-50%);
    z-index: 2;
}
.tl-item:last-child::after { display: none; }
.tl-phase {
    font-size: 8pt;
    color: #888;
    margin-bottom: 0.1cm;
}
.tl-title {
    font-size: 10pt;
    font-weight: 700;
    color: #1a1a1a;
}
.tl-week {
    font-size: 8pt;
    color: #c41e3a;
    margin-top: 0.1cm;
}

/* ===== 进度条清单 ===== */
.checklist {
    margin: 0.3cm 0;
    page-break-inside: avoid;
}
.cl-row {
    display: flex;
    align-items: center;
    gap: 0.3cm;
    margin: 0.18cm 0;
    font-size: 9.5pt;
}
.cl-check {
    width: 16px;
    height: 16px;
    border: 2px solid #c41e3a;
    border-radius: 3px;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #c41e3a;
    font-size: 10pt;
    font-weight: 700;
}
.cl-track {
    flex: 1;
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
}
.cl-bar {
    height: 100%;
    background: linear-gradient(90deg, #c41e3a, #d4a017);
    border-radius: 4px;
}

/* ===== 页脚 ===== */
.footer-note {
    text-align: center;
    font-size: 8.5pt;
    color: #aaa;
    margin-top: 1.5cm;
    padding-top: 0.3cm;
    border-top: 1px solid #eee;
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
    <div class="cover-deco-circle"></div>
    <div class="cover-content">
        <div class="cover-tag">应聘补充资料</div>
        <h1>{title}</h1>
        <div class="cover-subtitle">{subtitle}</div>
    </div>
    <div class="cover-meta">生成日期：2026年6月13日</div>
    <div class="cover-accent"></div>
</div>
{body}
<div class="footer-note">本文件仅供应聘展示使用 · 数据来源：公开市场信息及一手样本分析</div>
</body>
</html>
"""


def extract_subtitle(md_text):
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
    subtitle = re.sub(r'\*\*(.*?)\*\*', r'\1', subtitle)
    return subtitle


def _insert(body, heading_keyword, html, prev_tag=None):
    idx = body.find('>' + heading_keyword)
    if idx == -1:
        idx = body.find(heading_keyword)
    if idx == -1:
        return body
    before = body[:idx]
    tags = [prev_tag] if prev_tag else ['</table>', '</ul>', '</ol>']
    for tag in tags:
        if tag:
            t = before.rfind(tag)
            if t != -1:
                pos = t + len(tag)
                return body[:pos] + '\n' + html + body[pos:]
    return body


def enhance_01(body):
    DASHBOARD = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">1.9%</div><div class="dash-label">社零增速</div><div class="dash-trend down">▼ 低位</div></div><div class="dash-card"><div class="dash-num">-37%</div><div class="dash-label">黄金消费同比</div><div class="dash-trend down">▼ 承压</div></div><div class="dash-card"><div class="dash-num">7→20</div><div class="dash-label">银价波动(元/克)</div><div class="dash-trend up">▲ 暴涨</div></div><div class="dash-card"><div class="dash-num">~1000</div><div class="dash-label">头部关店数</div><div class="dash-trend down">▼ 收缩</div></div></div>'''
    COST = '''<div class="viz-title">成本结构对比</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">传统纯银</span><div class="bar-track"><div class="bar-seg silver" style="width:75%"></div><div class="bar-seg copper" style="width:0%"></div><div class="bar-seg labor" style="width:12%"></div></div><span class="bar-pct">银75%+工12%</span></div><div class="bar-row"><span class="bar-label">错铜工艺</span><div class="bar-track"><div class="bar-seg silver" style="width:35%"></div><div class="bar-seg copper" style="width:12%"></div><div class="bar-seg labor" style="width:30%"></div></div><span class="bar-pct">银35%+铜12%+工30%</span></div></div><div class="bar-legend"><span class="leg-dot silver"></span>银料 <span class="leg-dot copper"></span>铜料 <span class="leg-dot labor"></span>人工</div>'''
    THREAT = '''<div class="viz-title">五类玩家威胁度</div><div class="threat-chart"><div class="t-row"><span class="t-name">头部文创</span><div class="t-track"><div class="t-bar t5" style="width:100%"></div></div><span class="t-pct">极高</span></div><div class="t-row"><span class="t-name">非遗传承</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div><div class="t-row"><span class="t-name">设计师DTC</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div><div class="t-row"><span class="t-name">区域老字号</span><div class="t-track"><div class="t-bar t2" style="width:40%"></div></div><span class="t-pct">较低</span></div><div class="t-row"><span class="t-name">国际轻奢</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div></div>'''
    DONUT = '''<div class="viz-title">核心客群占比</div><div class="donut-wrap"><div class="donut" style="background: conic-gradient(#c41e3a 0% 40%, #e66 40% 70%, #f88 70% 85%, #fcc 85% 100%);"></div><div class="donut-legend"><div class="d-leg"><span class="d-dot" style="background:#c41e3a"></span>Z世代国潮追随者 40%</div><div class="d-leg"><span class="d-dot" style="background:#e66"></span>新锐白领 30%</div><div class="d-leg"><span class="d-dot" style="background:#f88"></span>玄学功能需求者 15%</div><div class="d-leg"><span class="d-dot" style="background:#fcc"></span>高净值收藏者 10%</div></div></div>'''
    MATRIX = '''<div class="viz-title">产品矩阵</div><div class="matrix-three"><div class="m-card"><div class="m-tier">入门引流</div><div class="m-name">云纹</div><div class="m-price">200-400元</div><div class="m-scene">日常佩戴 / 送礼</div></div><div class="m-card m-main"><div class="m-tier">主力利润</div><div class="m-name">山海</div><div class="m-price">400-800元</div><div class="m-scene">本命年 / 职场开运</div></div><div class="m-card m-lux"><div class="m-tier">限量收藏</div><div class="m-name">乾坤</div><div class="m-price">800-2000元</div><div class="m-scene">收藏 / 高端送礼</div></div></div>'''
    PIE = '''<div class="viz-title">渠道预算分配</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 30%, #c41e3a 30% 55%, #d44 55% 75%, #f55 75% 90%, #faa 90% 95%, #fee 95% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>淘宝/天猫 30%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>抖音 25%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>小红书 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>微信私域 15%</div><div class="p-leg"><span class="p-dot" style="background:#faa"></span>B站 5%</div><div class="p-leg"><span class="p-dot" style="background:#fee"></span>出海 5%</div></div></div>'''
    GMV = '''<div class="viz-title">首年月度GMV预测（万元）</div><div class="gmv-chart"><div class="g-col"><div class="g-bar" style="height:35%"></div><span class="g-label">Q1</span><span class="g-val">22</span></div><div class="g-col"><div class="g-bar" style="height:55%"></div><span class="g-label">Q2</span><span class="g-val">42</span></div><div class="g-col"><div class="g-bar" style="height:75%"></div><span class="g-label">Q3</span><span class="g-val">63</span></div><div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">Q4</span><span class="g-val">105</span></div></div><div class="gmv-total">全年目标 <strong>300万</strong>（含10%安全余量）</div>'''
    body = _insert(body, '1.3 研究结论', DASHBOARD)
    body = _insert(body, '2.2.3 局限性', COST)
    body = _insert(body, '3.2 头部品牌弱点拆解', THREAT)
    body = _insert(body, '4.2 消费趋势演变', DONUT, '</ul>')
    body = _insert(body, '5.3 上新节奏建议', MATRIX)
    body = _insert(body, '6.3 内容增长飞轮', PIE)
    body = _insert(body, '考虑退货率（20%）及保守修正', GMV)
    return body


def enhance_02(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">90天</div><div class="dash-label">落地周期</div><div class="dash-trend up">▲ 三阶段</div></div><div class="dash-card"><div class="dash-num">5维</div><div class="dash-label">能力评估</div><div class="dash-trend up">▲ 全覆盖</div></div><div class="dash-card"><div class="dash-num">4岗</div><div class="dash-label">岗位侧重</div><div class="dash-trend up">▲ 差异化</div></div><div class="dash-card"><div class="dash-num">12项</div><div class="dash-label">关键交付</div><div class="dash-trend up">▲ 可追踪</div></div></div>'''
    TIMELINE = '''<div class="viz-title">三阶段落地路径</div><div class="timeline"><div class="tl-item"><div class="tl-phase">第一阶段</div><div class="tl-title">调研诊断</div><div class="tl-week">Day 0-30</div></div><div class="tl-item"><div class="tl-phase">第二阶段</div><div class="tl-title">策略输出</div><div class="tl-week">Day 31-60</div></div><div class="tl-item"><div class="tl-phase">第三阶段</div><div class="tl-title">落地验证</div><div class="tl-week">Day 61-90</div></div></div>'''
    BAR = '''<div class="viz-title">各阶段时间投入占比</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">调研诊断</span><div class="bar-track"><div class="bar-seg silver" style="width:35%"></div></div><span class="bar-pct">35%</span></div><div class="bar-row"><span class="bar-label">策略输出</span><div class="bar-track"><div class="bar-seg copper" style="width:30%"></div></div><span class="bar-pct">30%</span></div><div class="bar-row"><span class="bar-label">落地验证</span><div class="bar-track"><div class="bar-seg labor" style="width:25%"></div></div><span class="bar-pct">25%</span></div><div class="bar-row"><span class="bar-label">复盘迭代</span><div class="bar-track"><div class="bar-seg" style="width:10%;background:#ccc"></div></div><span class="bar-pct">10%</span></div></div><div class="bar-legend"><span class="leg-dot silver"></span>调研 <span class="leg-dot copper"></span>策略 <span class="leg-dot labor"></span>验证 <span class="leg-dot" style="background:#ccc"></span>复盘</div>'''
    CARDS1 = '''<div class="viz-title">第一阶段关键交付</div><div class="card-row"><div class="g-card"><div class="g-title">行业调研</div><div class="g-desc">竞争格局与消费者画像</div></div><div class="g-card g2"><div class="g-title">数据爬取</div><div class="g-desc">产品结构与价格带分析</div></div><div class="g-card g3"><div class="g-title">用户访谈</div><div class="g-desc">10-15人深度访谈</div></div><div class="g-card g4"><div class="g-title">内部诊断</div><div class="g-desc">团队与供应链梳理</div></div></div>'''
    CARDS2 = '''<div class="viz-title">第二阶段关键交付</div><div class="card-row"><div class="g-card"><div class="g-title">产品策略</div><div class="g-desc">矩阵定位与上新节奏</div></div><div class="g-card g2"><div class="g-title">内容策略</div><div class="g-desc">选题模型与视觉规范</div></div><div class="g-card g3"><div class="g-title">渠道策略</div><div class="g-desc">平台选择与投放测试</div></div><div class="g-card g4"><div class="g-title">运营SOP</div><div class="g-desc">客服与售后标准流程</div></div></div>'''
    PIE = '''<div class="viz-title">资源分配比例</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 40%, #c41e3a 40% 65%, #d44 65% 85%, #f55 85% 95%, #faa 95% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>人力 40%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>投放 25%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>内容 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>工具 10%</div><div class="p-leg"><span class="p-dot" style="background:#faa"></span>其他 5%</div></div></div>'''
    CARDS3 = '''<div class="viz-title">第三阶段关键交付</div><div class="card-row"><div class="g-card"><div class="g-title">小规模上线</div><div class="g-desc">3-5款测款与数据复盘</div></div><div class="g-card g2"><div class="g-title">内容实测</div><div class="g-desc">10条笔记/视频投放</div></div><div class="g-card g3"><div class="g-title">数据复盘</div><div class="g-desc">转化率与ROI分析</div></div><div class="g-card g4"><div class="g-title">迭代方案</div><div class="g-desc">优化后规模化执行</div></div></div>'''
    GMV = '''<div class="viz-title">预期能力成长曲线</div><div class="gmv-chart"><div class="g-col"><div class="g-bar" style="height:25%"></div><span class="g-label">D1-30</span><span class="g-val">基线</span></div><div class="g-col"><div class="g-bar" style="height:50%"></div><span class="g-label">D31-60</span><span class="g-val">策略</span></div><div class="g-col"><div class="g-bar" style="height:75%"></div><span class="g-label">D61-90</span><span class="g-val">验证</span></div><div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">D90+</span><span class="g-val">成熟</span></div></div><div class="gmv-total">90天后预期 <strong>运营体系成型</strong></div>'''
    ABILITY = '''<div class="viz-title">五维能力评估</div><div class="card-row"><div class="g-card"><div class="g-title">产品定义</div><div class="g-num">★★★★★</div></div><div class="g-card g2"><div class="g-title">内容创意</div><div class="g-num">★★★★☆</div></div><div class="g-card g3"><div class="g-title">渠道运营</div><div class="g-num">★★★☆☆</div></div><div class="g-card g4"><div class="g-title">供应链</div><div class="g-num">★★★★☆</div></div><div class="g-card g5"><div class="g-title">数据分析</div><div class="g-num">★★★☆☆</div></div></div>'''
    ROLES = '''<div class="viz-title">不同岗位侧重</div><div class="card-row"><div class="g-card"><div class="g-title">品牌主理人</div><div class="g-desc">产品定义+供应链</div></div><div class="g-card g2"><div class="g-title">内容运营</div><div class="g-desc">创意+投放+用户</div></div><div class="g-card g3"><div class="g-title">电商运营</div><div class="g-desc">渠道+数据+活动</div></div><div class="g-card g4"><div class="g-title">视觉设计</div><div class="g-desc">拍摄+详情页+包装</div></div></div>'''
    body = _insert(body, '一、研究框架', DASH)
    body = _insert(body, '二、第一阶段：调研诊断', TIMELINE)
    body = _insert(body, '2.2 具体动作与交付物', BAR)
    body = _insert(body, '三、第二阶段：策略输出', CARDS1)
    body = _insert(body, '3.2 具体动作与交付物', PIE)
    body = _insert(body, '四、第三阶段：落地验证', CARDS2)
    body = _insert(body, '4.2 具体动作与交付物', GMV)
    body = _insert(body, '五、能力评估维度总览', CARDS3)
    body = _insert(body, '六、不同岗位的侧重点调整', ABILITY)
    body = _insert(body, '本文件仅供应聘展示使用', ROLES)
    return body


def enhance_03(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">2.5亿</div><div class="dash-label">小红书月活</div><div class="dash-trend up">▲ 精准</div></div><div class="dash-card"><div class="dash-num">7亿</div><div class="dash-label">抖音月活</div><div class="dash-trend up">▲ 爆发</div></div><div class="dash-card"><div class="dash-num">6-12月</div><div class="dash-label">笔记生命周期</div><div class="dash-trend up">▲ 长尾</div></div><div class="dash-card"><div class="dash-num">48h</div><div class="dash-label">抖音内容半衰期</div><div class="dash-trend down">▼ 短平快</div></div></div>'''
    MODELS = '''<div class="viz-title">三类高转化内容模型</div><div class="matrix-three"><div class="m-card"><div class="m-tier">种草型</div><div class="m-name">产品种草</div><div class="m-price">强调工艺与细节</div><div class="m-scene">开箱 / 佩戴展示</div></div><div class="m-card m-main"><div class="m-tier">文化型</div><div class="m-name">文化科普</div><div class="m-price">错铜工艺与寓意</div><div class="m-scene">匠人故事 / 历史</div></div><div class="m-card m-lux"><div class="m-tier">场景型</div><div class="m-name">场景穿搭</div><div class="m-price">穿搭与场景融合</div><div class="m-scene">OOTD / 节日送礼</div></div></div>'''
    PIE = '''<div class="viz-title">内容团队时间分配</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 30%, #c41e3a 30% 55%, #d44 55% 75%, #f55 75% 90%, #faa 90% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>内容策划 30%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>拍摄制作 25%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>账号运营 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>数据分析 15%</div><div class="p-leg"><span class="p-dot" style="background:#faa"></span>投放优化 10%</div></div></div>'''
    PLATFORMS = '''<div class="viz-title">双平台策略对比</div><div class="card-row"><div class="g-card"><div class="g-title">小红书</div><div class="g-num">图文+搜索</div><div class="g-desc">种草决策 / 长尾流量</div></div><div class="g-card g2"><div class="g-title">抖音</div><div class="g-num">视频+直播</div><div class="g-desc">爆发打品 / 匠人IP</div></div></div>'''
    BAR = '''<div class="viz-title">双平台核心指标对比</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">转化率</span><div class="bar-track"><div class="bar-seg silver" style="width:35%"></div><div class="bar-seg copper" style="width:25%"></div></div><span class="bar-pct">小红书 3.5% / 抖音 2.5%</span></div><div class="bar-row"><span class="bar-label">互动率</span><div class="bar-track"><div class="bar-seg silver" style="width:28%"></div><div class="bar-seg copper" style="width:45%"></div></div><span class="bar-pct">小红书 2.8% / 抖音 4.5%</span></div><div class="bar-row"><span class="bar-label">客单价</span><div class="bar-track"><div class="bar-seg silver" style="width:60%"></div><div class="bar-seg copper" style="width:40%"></div></div><span class="bar-pct">小红书 600元 / 抖音 400元</span></div><div class="bar-row"><span class="bar-label">复购率</span><div class="bar-track"><div class="bar-seg silver" style="width:25%"></div><div class="bar-seg copper" style="width:15%"></div></div><span class="bar-pct">小红书 25% / 抖音 15%</span></div></div><div class="bar-legend"><span class="leg-dot silver"></span>小红书 <span class="leg-dot copper"></span>抖音</div>'''
    FORMULA = '''<div class="viz-title">选题公式</div><div class="dashboard"><div class="dash-card"><div class="dash-num">人群</div><div class="dash-label">Z世代 / 新锐白领</div></div><div class="dash-card"><div class="dash-num">×</div><div class="dash-label">痛点</div></div><div class="dash-card"><div class="dash-num">×</div><div class="dash-label">文化符号</div></div><div class="dash-card"><div class="dash-num">×</div><div class="dash-label">视觉差异</div></div></div>'''
    TIMELINE = '''<div class="viz-title">月度内容发布节奏</div><div class="timeline"><div class="tl-item"><div class="tl-phase">Week 1-2</div><div class="tl-title">预热蓄水</div><div class="tl-week">种草笔记+达人合作</div></div><div class="tl-item"><div class="tl-phase">Week 3</div><div class="tl-title">集中爆发</div><div class="tl-week">直播+短视频高密度</div></div><div class="tl-item"><div class="tl-phase">Week 4</div><div class="tl-title">长尾收割</div><div class="tl-week">搜索优化+私域沉淀</div></div></div>'''
    body = _insert(body, '1.2 研究方法', DASH)
    body = _insert(body, '2.2 三类高转化内容模型', MODELS)
    body = _insert(body, '2.3 选题公式', PIE)
    body = _insert(body, '3.2 匠人IP账号模型', PLATFORMS)
    body = _insert(body, '3.3 直播话术结构样本', BAR)
    body = _insert(body, '4.1 内容分发节奏', FORMULA)
    body = _insert(body, '4.2 内容复用矩阵', TIMELINE)
    return body


def enhance_04(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">3层</div><div class="dash-label">供应链架构</div><div class="dash-trend up">▲ 完整</div></div><div class="dash-card"><div class="dash-num">100元</div><div class="dash-label">单位成本</div><div class="dash-trend down">▼ 可控</div></div><div class="dash-card"><div class="dash-num">5项</div><div class="dash-label">考察维度</div><div class="dash-trend up">▲ 系统</div></div><div class="dash-card"><div class="dash-num">3阶</div><div class="dash-label">分阶段配置</div><div class="dash-trend up">▲ 渐进</div></div></div>'''
    FLOW = '''<div class="viz-title">供应链三层架构</div><div class="timeline"><div class="tl-item"><div class="tl-phase">Layer 1</div><div class="tl-title">原材料</div><div class="tl-week">银料+铜料</div></div><div class="tl-item"><div class="tl-phase">Layer 2</div><div class="tl-title">核心制造</div><div class="tl-week">錾刻+铸造</div></div><div class="tl-item"><div class="tl-phase">Layer 3</div><div class="tl-title">表面处理</div><div class="tl-week">氧化+检测</div></div></div>'''
    COST = '''<div class="viz-title">单位成本拆解（错铜手镯）</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">银料</span><div class="bar-track"><div class="bar-seg silver" style="width:35%"></div></div><span class="bar-pct">35元</span></div><div class="bar-row"><span class="bar-label">铜料</span><div class="bar-track"><div class="bar-seg copper" style="width:12%"></div></div><span class="bar-pct">12元</span></div><div class="bar-row"><span class="bar-label">人工</span><div class="bar-track"><div class="bar-seg labor" style="width:30%"></div></div><span class="bar-pct">30元</span></div><div class="bar-row"><span class="bar-label">其他</span><div class="bar-track"><div class="bar-seg" style="width:23%;background:#ccc"></div></div><span class="bar-pct">23元</span></div></div><div class="bar-legend"><span class="leg-dot silver"></span>银料 <span class="leg-dot copper"></span>铜料 <span class="leg-dot labor"></span>人工 <span class="leg-dot" style="background:#ccc"></span>其他</div>'''
    STAGES = '''<div class="viz-title">分阶段供应链配置</div><div class="matrix-three"><div class="m-card"><div class="m-tier">启动期</div><div class="m-name">小批量验证</div><div class="m-price">3-5款</div><div class="m-scene">手工工坊 / 灵活</div></div><div class="m-card m-main"><div class="m-tier">增长期</div><div class="m-name">规模化</div><div class="m-price">10-20款</div><div class="m-scene">签约工厂 / 稳定</div></div><div class="m-card m-lux"><div class="m-tier">稳定期</div><div class="m-name">纵深整合</div><div class="m-price">全矩阵</div><div class="m-scene">自有工坊 / 壁垒</div></div></div>'''
    PIE = '''<div class="viz-title">错铜手镯成本占比</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 35%, #c41e3a 35% 47%, #d44 47% 77%, #f55 77% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>银料 35%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>铜料 12%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>人工 30%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>其他 23%</div></div></div>'''
    CHECK = '''<div class="viz-title">供应商考察Checklist</div><div class="checklist"><div class="cl-row"><span class="cl-check">✓</span><span>样品工艺还原度</span><div class="cl-track"><div class="cl-bar" style="width:100%"></div></div></div><div class="cl-row"><span class="cl-check">✓</span><span>交期稳定性</span><div class="cl-track"><div class="cl-bar" style="width:90%"></div></div></div><div class="cl-row"><span class="cl-check">✓</span><span>最小起订量(MOQ)</span><div class="cl-track"><div class="cl-bar" style="width:80%"></div></div></div><div class="cl-row"><span class="cl-check">✓</span><span>银料纯度检测报告</span><div class="cl-track"><div class="cl-bar" style="width:100%"></div></div></div><div class="cl-row"><span class="cl-check">✓</span><span>环保与合规资质</span><div class="cl-track"><div class="cl-bar" style="width:85%"></div></div></div></div>'''
    GMV = '''<div class="viz-title">首年月度采购成本预测（万元）</div><div class="gmv-chart"><div class="g-col"><div class="g-bar" style="height:20%"></div><span class="g-label">Q1</span><span class="g-val">5</span></div><div class="g-col"><div class="g-bar" style="height:45%"></div><span class="g-label">Q2</span><span class="g-val">12</span></div><div class="g-col"><div class="g-bar" style="height:70%"></div><span class="g-label">Q3</span><span class="g-val">20</span></div><div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">Q4</span><span class="g-val">35</span></div></div><div class="gmv-total">全年采购预算 <strong>72万</strong></div>'''
    body = _insert(body, '一、错铜工艺供应链全景图', DASH)
    body = _insert(body, '1.2 供应链核心环节拆解', FLOW)
    body = _insert(body, '二、核心环节供应商分析', COST)
    body = _insert(body, '三、供应链分阶段配置建议', STAGES)
    body = _insert(body, '四、成本结构测算模型', PIE)
    body = _insert(body, '五、供应商考察Checklist', CHECK)
    body = _insert(body, '本文件仅供应聘展示使用', GMV)
    return body


def enhance_05(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">5类</div><div class="dash-label">核心风险</div><div class="dash-trend up">▲ 全覆盖</div></div><div class="dash-card"><div class="dash-num">2项</div><div class="dash-label">红色预警</div><div class="dash-trend up">▲ 高危</div></div><div class="dash-card"><div class="dash-num">3层</div><div class="dash-label">响应架构</div><div class="dash-trend up">▲ 分级</div></div><div class="dash-card"><div class="dash-num">24h</div><div class="dash-label">黄金响应</div><div class="dash-trend up">▲ 时效</div></div></div>'''
    RISKS = '''<div class="viz-title">五类核心风险概览</div><div class="card-row"><div class="g-card"><div class="g-title">银价波动</div><div class="g-num">高危</div><div class="g-desc">原料成本剧烈波动</div></div><div class="g-card g2"><div class="g-title">竞品跟进</div><div class="g-num">中危</div><div class="g-desc">差异化窗口期有限</div></div><div class="g-card g3"><div class="g-title">质量舆情</div><div class="g-num">高危</div><div class="g-desc">过敏/氧化负面传播</div></div><div class="g-card g4"><div class="g-title">宗教合规</div><div class="g-num">中危</div><div class="g-desc">敏感符号与法规</div></div><div class="g-card g5"><div class="g-title">平台规则</div><div class="g-num">低危</div><div class="g-desc">流量政策与算法</div></div></div>'''
    BAR = '''<div class="viz-title">各类风险潜在损失对比（万元/年）</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">银价波动</span><div class="bar-track"><div class="t-bar t5" style="width:100%"></div></div><span class="bar-pct">50万</span></div><div class="bar-row"><span class="bar-label">质量舆情</span><div class="bar-track"><div class="t-bar t5" style="width:80%"></div></div><span class="bar-pct">40万</span></div><div class="bar-row"><span class="bar-label">竞品跟进</span><div class="bar-track"><div class="t-bar t3" style="width:50%"></div></div><span class="bar-pct">25万</span></div><div class="bar-row"><span class="bar-label">宗教合规</span><div class="bar-track"><div class="t-bar t3" style="width:40%"></div></div><span class="bar-pct">20万</span></div><div class="bar-row"><span class="bar-label">平台规则</span><div class="bar-track"><div class="t-bar t2" style="width:20%"></div></div><span class="bar-pct">10万</span></div></div>'''
    PIE = '''<div class="viz-title">年度风险预算分配</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 40%, #c41e3a 40% 65%, #d44 65% 85%, #f55 85% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>预防投入 40%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>应急响应 25%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>保险覆盖 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>储备金 15%</div></div></div>'''
    LIGHT = '''<div class="viz-title">风险分级状态</div><div class="threat-chart"><div class="t-row"><span class="t-name">银价波动</span><div class="t-track"><div class="t-bar t5" style="width:100%"></div></div><span class="t-pct">红色预警</span></div><div class="t-row"><span class="t-name">质量舆情</span><div class="t-track"><div class="t-bar t5" style="width:100%"></div></div><span class="t-pct">红色预警</span></div><div class="t-row"><span class="t-name">竞品跟进</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">黄色关注</span></div><div class="t-row"><span class="t-name">宗教合规</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">黄色关注</span></div><div class="t-row"><span class="t-name">平台规则</span><div class="t-track"><div class="t-bar t2" style="width:40%"></div></div><span class="t-pct">蓝色常规</span></div></div>'''
    ORG = '''<div class="viz-title">危机响应组织架构</div><div class="timeline"><div class="tl-item"><div class="tl-phase">决策层</div><div class="tl-title">品牌主理人</div><div class="tl-week">最终决策</div></div><div class="tl-item"><div class="tl-phase">执行层</div><div class="tl-title">运营+客服</div><div class="tl-week">一线响应</div></div><div class="tl-item"><div class="tl-phase">支持层</div><div class="tl-title">法务+供应链</div><div class="tl-week">专业支撑</div></div></div>'''
    body = _insert(body, '一、银价波动风险', DASH)
    body = _insert(body, '二、竞品快速跟进风险', RISKS)
    body = _insert(body, '三、产品质量舆情风险', BAR)
    body = _insert(body, '四、宗教文创合规风险', PIE)
    body = _insert(body, '六、风险响应组织架构建议', LIGHT)
    body = _insert(body, '本文件仅供应聘展示使用', ORG)
    return body


def enhance_06(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">6.6亿</div><div class="dash-label">东南亚人口</div><div class="dash-trend up">▲ 红利</div></div><div class="dash-card"><div class="dash-num">$2.5T</div><div class="dash-label">GDP总量</div><div class="dash-trend up">▲ 增长</div></div><div class="dash-card"><div class="dash-num">25%</div><div class="dash-label">电商增速</div><div class="dash-trend up">▲ 高速</div></div><div class="dash-card"><div class="dash-num">$50B</div><div class="dash-label">电商市场规模</div><div class="dash-trend up">▲ 蓝海</div></div></div>'''
    PRIORITY = '''<div class="viz-title">六国市场优先级</div><div class="threat-chart"><div class="t-row"><span class="t-name">印尼</span><div class="t-track"><div class="t-bar t5" style="width:100%"></div></div><span class="t-pct">P0 最高</span></div><div class="t-row"><span class="t-name">越南</span><div class="t-track"><div class="t-bar t5" style="width:85%"></div></div><span class="t-pct">P1 高</span></div><div class="t-row"><span class="t-name">泰国</span><div class="t-track"><div class="t-bar t3" style="width:70%"></div></div><span class="t-pct">P1 高</span></div><div class="t-row"><span class="t-name">菲律宾</span><div class="t-track"><div class="t-bar t3" style="width:55%"></div></div><span class="t-pct">P2 中</span></div><div class="t-row"><span class="t-name">马来西亚</span><div class="t-track"><div class="t-bar t2" style="width:40%"></div></div><span class="t-pct">P2 中</span></div><div class="t-row"><span class="t-name">新加坡</span><div class="t-track"><div class="t-bar t2" style="width:25%"></div></div><span class="t-pct">P3 低</span></div></div>'''
    COMPARE = '''<div class="viz-title">双平台进入策略</div><div class="card-row"><div class="g-card"><div class="g-title">Shopee</div><div class="g-num">东南亚电商</div><div class="g-desc">货架电商 / 搜索流量</div></div><div class="g-card g2"><div class="g-title">TikTok Shop</div><div class="g-num">内容电商</div><div class="g-desc">短视频+直播 / 爆发</div></div></div>'''
    LOGISTICS = '''<div class="viz-title">物流方案对比</div><div class="matrix-three"><div class="m-card"><div class="m-tier">国内直邮</div><div class="m-name">轻资产</div><div class="m-price">适合测款</div><div class="m-scene">时效7-15天</div></div><div class="m-card m-main"><div class="m-tier">海外仓</div><div class="m-name">重体验</div><div class="m-price">适合爆款</div><div class="m-scene">时效2-3天</div></div><div class="m-card m-lux"><div class="m-tier">本地生产</div><div class="m-name">长期壁垒</div><div class="m-price">适合规模化</div><div class="m-scene">深度本地化</div></div></div>'''
    BAR = '''<div class="viz-title">物流成本对比（元/kg）</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">国内直邮</span><div class="bar-track"><div class="bar-seg silver" style="width:40%"></div></div><span class="bar-pct">80元</span></div><div class="bar-row"><span class="bar-label">海运拼箱</span><div class="bar-track"><div class="bar-seg copper" style="width:25%"></div></div><span class="bar-pct">50元</span></div><div class="bar-row"><span class="bar-label">海外仓头程</span><div class="bar-track"><div class="bar-seg labor" style="width:20%"></div></div><span class="bar-pct">35元</span></div><div class="bar-row"><span class="bar-label">本地生产</span><div class="bar-track"><div class="bar-seg" style="width:15%;background:#ccc"></div></div><span class="bar-pct">15元</span></div></div><div class="bar-legend"><span class="leg-dot silver"></span>直邮 <span class="leg-dot copper"></span>海运 <span class="leg-dot labor"></span>海外仓 <span class="leg-dot" style="background:#ccc"></span>本地</div>'''
    TIMELINE = '''<div class="viz-title">首年启动路径</div><div class="timeline"><div class="tl-item"><div class="tl-phase">Q1</div><div class="tl-title">账号搭建</div><div class="tl-week">店铺+资质</div></div><div class="tl-item"><div class="tl-phase">Q2</div><div class="tl-title">测款跑通</div><div class="tl-week">3-5款测试</div></div><div class="tl-item"><div class="tl-phase">Q3</div><div class="tl-title">内容起量</div><div class="tl-week">KOL+直播</div></div><div class="tl-item"><div class="tl-phase">Q4</div><div class="tl-title">规模化</div><div class="tl-week">爆品+复购</div></div></div>'''
    BUDGET = '''<div class="viz-title">首年预算分配</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 35%, #c41e3a 35% 55%, #d44 55% 75%, #f55 75% 90%, #faa 90% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>产品开发 35%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>内容投放 20%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>物流仓储 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>平台费用 15%</div><div class="p-leg"><span class="p-dot" style="background:#faa"></span>应急储备 10%</div></div></div>'''
    GMV = '''<div class="viz-title">首年GMV增长预测（万元）</div><div class="gmv-chart"><div class="g-col"><div class="g-bar" style="height:10%"></div><span class="g-label">Q1</span><span class="g-val">5</span></div><div class="g-col"><div class="g-bar" style="height:30%"></div><span class="g-label">Q2</span><span class="g-val">15</span></div><div class="g-col"><div class="g-bar" style="height:60%"></div><span class="g-label">Q3</span><span class="g-val">30</span></div><div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">Q4</span><span class="g-val">50</span></div></div><div class="gmv-total">首年目标GMV <strong>100万</strong></div>'''
    body = _insert(body, '二、目标市场选择与竞争环境', DASH)
    body = _insert(body, '2.2 竞争环境扫描', PRIORITY)
    body = _insert(body, '3.1 Shopee 运营策略', COMPARE)
    body = _insert(body, '5.1 物流模式对比', LOGISTICS)
    body = _insert(body, '5.2 物流成本测算', BAR)
    body = _insert(body, '6.1 首年启动路径', TIMELINE)
    body = _insert(body, '6.2 预算测算', BUDGET)
    body = _insert(body, '本文件仅供应聘展示使用', GMV)
    return body


def enhance_07(body):
    DASH = '''<div class="dashboard"><div class="dash-card"><div class="dash-num">6步</div><div class="dash-label">实验方法论</div><div class="dash-trend up">▲ 闭环</div></div><div class="dash-card"><div class="dash-num">7类</div><div class="dash-label">核心实验</div><div class="dash-trend up">▲ 全链路</div></div><div class="dash-card"><div class="dash-num">95%</div><div class="dash-label">置信度</div><div class="dash-trend up">▲ 科学</div></div><div class="dash-card"><div class="dash-num">7天</div><div class="dash-label">最小周期</div><div class="dash-trend up">▲ 严谨</div></div></div>'''
    FLOW = '''<div class="viz-title">六步实验方法论</div><div class="timeline"><div class="tl-item"><div class="tl-phase">Step 1</div><div class="tl-title">定义假设</div><div class="tl-week">明确变量</div></div><div class="tl-item"><div class="tl-phase">Step 2</div><div class="tl-title">设计实验</div><div class="tl-week">控制变量</div></div><div class="tl-item"><div class="tl-phase">Step 3</div><div class="tl-title">分配流量</div><div class="tl-week">随机分组</div></div><div class="tl-item"><div class="tl-phase">Step 4</div><div class="tl-title">采集数据</div><div class="tl-week">埋点追踪</div></div><div class="tl-item"><div class="tl-phase">Step 5</div><div class="tl-title">统计检验</div><div class="tl-week">显著性判断</div></div><div class="tl-item"><div class="tl-phase">Step 6</div><div class="tl-title">决策落地</div><div class="tl-week">规模化或迭代</div></div></div>'''
    EXPERIMENTS = '''<div class="viz-title">七类核心实验</div><div class="card-row"><div class="g-card"><div class="g-title">主图实验</div><div class="g-desc">点击率优化</div></div><div class="g-card g2"><div class="g-title">标题实验</div><div class="g-desc">搜索流量优化</div></div><div class="g-card g3"><div class="g-title">价格实验</div><div class="g-desc">弹性与利润平衡</div></div><div class="g-card g4"><div class="g-title">详情页实验</div><div class="g-desc">转化率优化</div></div></div><div class="card-row"><div class="g-card"><div class="g-title">投放实验</div><div class="g-desc">ROI与出价策略</div></div><div class="g-card g2"><div class="g-title">直播实验</div><div class="g-desc">话术与节奏</div></div><div class="g-card g3"><div class="g-title">私域实验</div><div class="g-desc">复购与裂变</div></div></div>'''
    BAR = '''<div class="viz-title">七类实验样本需求（UV）</div><div class="bar-compare"><div class="bar-row"><span class="bar-label">主图</span><div class="bar-track"><div class="bar-seg silver" style="width:25%"></div></div><span class="bar-pct">500</span></div><div class="bar-row"><span class="bar-label">标题</span><div class="bar-track"><div class="bar-seg copper" style="width:40%"></div></div><span class="bar-pct">800</span></div><div class="bar-row"><span class="bar-label">价格</span><div class="bar-track"><div class="bar-seg labor" style="width:60%"></div></div><span class="bar-pct">1,200</span></div><div class="bar-row"><span class="bar-label">详情页</span><div class="bar-track"><div class="bar-seg" style="width:80%;background:#ccc"></div></div><span class="bar-pct">1,600</span></div><div class="bar-row"><span class="bar-label">投放</span><div class="bar-track"><div class="bar-seg silver" style="width:50%"></div></div><span class="bar-pct">1,000</span></div><div class="bar-row"><span class="bar-label">直播</span><div class="bar-track"><div class="bar-seg copper" style="width:100%"></div></div><span class="bar-pct">2,000</span></div><div class="bar-row"><span class="bar-label">私域</span><div class="bar-track"><div class="bar-seg labor" style="width:35%"></div></div><span class="bar-pct">700</span></div></div>'''
    PIE = '''<div class="viz-title">实验资源分配</div><div class="pie-wrap"><div class="pie" style="background: conic-gradient(#8B0000 0% 30%, #c41e3a 30% 50%, #d44 50% 70%, #f55 70% 85%, #faa 85% 100%);"></div><div class="pie-legend"><div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>技术开发 30%</div><div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>流量采买 20%</div><div class="p-leg"><span class="p-dot" style="background:#d44"></span>人力分析 20%</div><div class="p-leg"><span class="p-dot" style="background:#f55"></span>工具订阅 15%</div><div class="p-leg"><span class="p-dot" style="background:#faa"></span>迭代储备 15%</div></div></div>'''
    MISTAKES = '''<div class="viz-title">常见实施误区</div><div class="matrix-three"><div class="m-card"><div class="m-tier">误区</div><div class="m-name">样本不足</div><div class="m-price">过早下结论</div><div class="m-scene">需达最小样本量</div></div><div class="m-card m-main"><div class="m-tier">误区</div><div class="m-name">变量混杂</div><div class="m-price">多变量同时改</div><div class="m-scene">控制单一变量</div></div><div class="m-card m-lux"><div class="m-tier">误区</div><div class="m-name">周期过短</div><div class="m-price">未覆盖完整周期</div><div class="m-scene">至少7天数据</div></div></div>'''
    GMV = '''<div class="viz-title">实验驱动增长曲线</div><div class="gmv-chart"><div class="g-col"><div class="g-bar" style="height:20%"></div><span class="g-label">M1</span><span class="g-val">基线</span></div><div class="g-col"><div class="g-bar" style="height:40%"></div><span class="g-label">M2</span><span class="g-val">+15%</span></div><div class="g-col"><div class="g-bar" style="height:65%"></div><span class="g-label">M3</span><span class="g-val">+35%</span></div><div class="g-col"><div class="g-bar" style="height:85%"></div><span class="g-label">M4</span><span class="g-val">+55%</span></div><div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">M5</span><span class="g-val">+80%</span></div></div><div class="gmv-total">持续实验预期 <strong>转化率提升80%</strong></div>'''
    body = _insert(body, '一、研究背景与方法论', DASH)
    body = _insert(body, '1.2 实验设计的五条基本原则', FLOW)
    body = _insert(body, '2.1 主图点击率测试', EXPERIMENTS)
    body = _insert(body, '三、流量分配与实验周期', BAR)
    body = _insert(body, '四、数据收集与统计检验', PIE)
    body = _insert(body, '五、常见实施误区', MISTAKES)
    body = _insert(body, '本文件仅供应聘展示使用', GMV)
    return body


ENHANCE_MAP = {
    '01_': enhance_01,
    '02_': enhance_02,
    '03_': enhance_03,
    '04_': enhance_04,
    '05_': enhance_05,
    '06_': enhance_06,
    '07_': enhance_07,
}


def convert(md_path, out_dir):
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title = os.path.splitext(os.path.basename(md_path))[0]
    body_html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    subtitle = extract_subtitle(md_text)

    for prefix, fn in ENHANCE_MAP.items():
        if prefix in title:
            body_html = fn(body_html)
            break

    html = HTML_TEMPLATE.format(title=title, css=CSS, body=body_html, subtitle=subtitle)

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
