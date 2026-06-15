import re

html_path = r"g:\Downloads\蔡规划\应聘补充资料\01_中高端国潮错铜银饰赛道可行性研究.html"
out_path = html_path

with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 提取 subtitle
subtitle_m = re.search(r'<div class="cover-subtitle">(.*?)</div>', content, re.DOTALL)
subtitle = subtitle_m.group(1) if subtitle_m else ''
if not subtitle:
    subtitle_m = re.search(r'<div class="subtitle">(.*?)</div>', content, re.DOTALL)
    subtitle = subtitle_m.group(1) if subtitle_m else ''

# 提取正文
body_m = re.search(r'<body>(.*?)</body>', content, re.DOTALL)
full_body = body_m.group(1)

# 去掉旧的cover（如果有）
cover_end = full_body.find('<h1 id=')
if cover_end == -1:
    cover_end = full_body.find('<h1>')
main_content = full_body[cover_end:].strip()

# 找到 footer
footer_start = main_content.rfind('<div class="footer-note">')
footer_html = main_content[footer_start:]
main_content = main_content[:footer_start].strip()

title = "中高端国潮错铜银饰赛道可行性研究"

# ===== 可视化组件 HTML =====

DASHBOARD = '''
<div class="dashboard">
  <div class="dash-card"><div class="dash-num">1.9%</div><div class="dash-label">社零增速</div><div class="dash-trend down">▼ 低位</div></div>
  <div class="dash-card"><div class="dash-num">-37%</div><div class="dash-label">黄金消费同比</div><div class="dash-trend down">▼ 承压</div></div>
  <div class="dash-card"><div class="dash-num">7→20</div><div class="dash-label">银价波动(元/克)</div><div class="dash-trend up">▲ 暴涨</div></div>
  <div class="dash-card"><div class="dash-num">~1000</div><div class="dash-label">头部关店数</div><div class="dash-trend down">▼ 收缩</div></div>
</div>
'''

COST_BARS = '''
<div class="viz-title">成本结构对比</div>
<div class="bar-compare">
  <div class="bar-row"><span class="bar-label">传统纯银</span><div class="bar-track"><div class="bar-seg silver" style="width:75%"></div><div class="bar-seg copper" style="width:0%"></div><div class="bar-seg labor" style="width:12%"></div></div><span class="bar-pct">银75%+工12%</span></div>
  <div class="bar-row"><span class="bar-label">错铜工艺</span><div class="bar-track"><div class="bar-seg silver" style="width:35%"></div><div class="bar-seg copper" style="width:12%"></div><div class="bar-seg labor" style="width:30%"></div></div><span class="bar-pct">银35%+铜12%+工30%</span></div>
</div>
<div class="bar-legend"><span class="leg-dot silver"></span>银料 <span class="leg-dot copper"></span>铜料 <span class="leg-dot labor"></span>人工</div>
'''

THREAT_BARS = '''
<div class="viz-title">五类玩家威胁度</div>
<div class="threat-chart">
  <div class="t-row"><span class="t-name">头部文创</span><div class="t-track"><div class="t-bar t5" style="width:100%"></div></div><span class="t-pct">极高</span></div>
  <div class="t-row"><span class="t-name">非遗传承</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div>
  <div class="t-row"><span class="t-name">设计师DTC</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div>
  <div class="t-row"><span class="t-name">区域老字号</span><div class="t-track"><div class="t-bar t2" style="width:40%"></div></div><span class="t-pct">较低</span></div>
  <div class="t-row"><span class="t-name">国际轻奢</span><div class="t-track"><div class="t-bar t3" style="width:60%"></div></div><span class="t-pct">中等</span></div>
</div>
'''

CUSTOMER_DONUT = '''
<div class="viz-title">核心客群占比</div>
<div class="donut-wrap">
  <div class="donut" style="background: conic-gradient(#c41e3a 0% 40%, #e66 40% 70%, #f88 70% 85%, #fcc 85% 100%);"></div>
  <div class="donut-legend">
    <div class="d-leg"><span class="d-dot" style="background:#c41e3a"></span>Z世代国潮追随者 40%</div>
    <div class="d-leg"><span class="d-dot" style="background:#e66"></span>新锐白领 30%</div>
    <div class="d-leg"><span class="d-dot" style="background:#f88"></span>玄学功能需求者 15%</div>
    <div class="d-leg"><span class="d-dot" style="background:#fcc"></span>高净值收藏者 10%</div>
  </div>
</div>
'''

CHANNEL_PIE = '''
<div class="viz-title">渠道预算分配</div>
<div class="pie-wrap">
  <div class="pie" style="background: conic-gradient(#8B0000 0% 30%, #c41e3a 30% 55%, #d44 55% 75%, #f55 75% 90%, #faa 90% 95%, #fee 95% 100%);"></div>
  <div class="pie-legend">
    <div class="p-leg"><span class="p-dot" style="background:#8B0000"></span>淘宝/天猫 30%</div>
    <div class="p-leg"><span class="p-dot" style="background:#c41e3a"></span>抖音 25%</div>
    <div class="p-leg"><span class="p-dot" style="background:#d44"></span>小红书 20%</div>
    <div class="p-leg"><span class="p-dot" style="background:#f55"></span>微信私域 15%</div>
    <div class="p-leg"><span class="p-dot" style="background:#faa"></span>B站 5%</div>
    <div class="p-leg"><span class="p-dot" style="background:#fee"></span>出海 5%</div>
  </div>
</div>
'''

GMV_BARS = '''
<div class="viz-title">首年月度GMV预测（万元）</div>
<div class="gmv-chart">
  <div class="g-col"><div class="g-bar" style="height:35%"></div><span class="g-label">Q1</span><span class="g-val">22</span></div>
  <div class="g-col"><div class="g-bar" style="height:55%"></div><span class="g-label">Q2</span><span class="g-val">42</span></div>
  <div class="g-col"><div class="g-bar" style="height:75%"></div><span class="g-label">Q3</span><span class="g-val">63</span></div>
  <div class="g-col"><div class="g-bar" style="height:100%"></div><span class="g-label">Q4</span><span class="g-val">105</span></div>
</div>
<div class="gmv-total">全年目标 <strong>300万</strong>（含10%安全余量）</div>
'''

MATRIX_CARDS = '''
<div class="viz-title">产品矩阵</div>
<div class="matrix-three">
  <div class="m-card"><div class="m-tier">入门引流</div><div class="m-name">云纹</div><div class="m-price">200-400元</div><div class="m-scene">日常佩戴 / 送礼</div></div>
  <div class="m-card m-main"><div class="m-tier">主力利润</div><div class="m-name">山海</div><div class="m-price">400-800元</div><div class="m-scene">本命年 / 职场开运</div></div>
  <div class="m-card m-lux"><div class="m-tier">限量收藏</div><div class="m-name">乾坤</div><div class="m-price">800-2000元</div><div class="m-scene">收藏 / 高端送礼</div></div>
</div>
'''

# ===== 插入可视化到正文 =====
# 1. 在 1.2 关键数据 表格后插入仪表盘
main_content = main_content.replace(
    '</table>\n<h3 id="13">1.3 研究结论</h3>',
    '</table>\n' + DASHBOARD + '\n<h3 id="13">1.3 研究结论</h3>'
)

# 2. 在 2.2.2 成本结构表格后插入条形图
main_content = main_content.replace(
    '</table>\n<h4 id="223">2.2.3 局限性</h4>',
    '</table>\n' + COST_BARS + '\n<h4 id="223">2.2.3 局限性</h4>'
)

# 3. 在 3.1 五类玩家表格后插入威胁度图
main_content = main_content.replace(
    '</table>\n<h3 id="32">3.2 头部品牌弱点拆解</h3>',
    '</table>\n' + THREAT_BARS + '\n<h3 id="32">3.2 头部品牌弱点拆解</h3>'
)

# 4. 在 4.1 客群分层后插入环形图
main_content = main_content.replace(
    '</ul>\n<h3 id="42">4.2 消费趋势演变</h3>',
    '</ul>\n' + CUSTOMER_DONUT + '\n<h3 id="42">4.2 消费趋势演变</h3>'
)

# 5. 在 5.2 产品矩阵表格后插入三列卡片
main_content = main_content.replace(
    '</table>\n<h3 id="53">5.3 上新节奏建议</h3>',
    '</table>\n' + MATRIX_CARDS + '\n<h3 id="53">5.3 上新节奏建议</h3>'
)

# 6. 在 6.2 渠道投入表格后插入饼图
main_content = main_content.replace(
    '</table>\n<h3 id="63">6.3 内容增长飞轮</h3>',
    '</table>\n' + CHANNEL_PIE + '\n<h3 id="63">6.3 内容增长飞轮</h3>'
)

# 7. 在 7.1 财务预测表格后插入柱状图
main_content = main_content.replace(
    '</table>\n<p>考虑退货率（20%）及保守修正',
    '</table>\n' + GMV_BARS + '\n<p>考虑退货率（20%）及保守修正'
)

# ===== 完整 HTML =====
new_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
@page {{
    size: A4;
    margin: 2cm 2cm 2.5cm 2cm;
    @top-center {{ content: string(doctitle); font-size: 8pt; color: #aaa; font-family: "PingFang SC", sans-serif; }}
    @bottom-center {{ content: counter(page); font-size: 8pt; color: #aaa; }}
}}
@page :first {{ @top-center {{ content: none; }} @bottom-center {{ content: none; }} }}

body {{
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 10.5pt;
    line-height: 1.8;
    color: #333;
    max-width: 21cm;
    margin: 0 auto;
    padding: 0;
}}

/* ===== 封面 ===== */
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
    border: 4px solid rgba(212,160,23,0.4);
    border-radius: 50%;
    z-index: 1;
}}
.cover-deco-circle {{
    position: absolute;
    top: 15%;
    right: 15%;
    width: 80px;
    height: 80px;
    background: rgba(212,160,23,0.15);
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

/* ===== 代码 ===== */
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

/* ===== 引用块 ===== */
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

/* ===== 列表 ===== */
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

/* ===== 分割线 ===== */
hr {{
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, #c41e3a, #d4a017, transparent);
    margin: 0.8cm 0;
    border-radius: 1px;
}}

/* ===== 可视化：仪表盘 ===== */
.dashboard {{
    display: flex;
    gap: 0.4cm;
    margin: 0.5cm 0 0.8cm 0;
    page-break-inside: avoid;
}}
.dash-card {{
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 3px solid #c41e3a;
    border-radius: 6px;
    padding: 0.4cm;
    text-align: center;
}}
.dash-num {{
    font-size: 18pt;
    font-weight: 700;
    color: #c41e3a;
    line-height: 1.1;
}}
.dash-label {{
    font-size: 8.5pt;
    color: #888;
    margin-top: 0.15cm;
}}
.dash-trend {{
    font-size: 8pt;
    margin-top: 0.1cm;
}}
.dash-trend.up {{ color: #c41e3a; }}
.dash-trend.down {{ color: #888; }}

/* ===== 可视化：堆叠条形图 ===== */
.viz-title {{
    font-size: 10pt;
    font-weight: 700;
    color: #8B0000;
    margin: 0.6cm 0 0.3cm 0;
    padding-left: 0.3cm;
    border-left: 3px solid #d4a017;
}}
.bar-compare {{
    margin: 0.3cm 0;
    page-break-inside: avoid;
}}
.bar-row {{
    display: flex;
    align-items: center;
    gap: 0.3cm;
    margin: 0.25cm 0;
}}
.bar-label {{
    font-size: 9pt;
    color: #555;
    width: 4.5em;
    text-align: right;
    flex-shrink: 0;
}}
.bar-track {{
    flex: 1;
    height: 18px;
    background: #f0f0f0;
    border-radius: 9px;
    overflow: hidden;
    display: flex;
}}
.bar-seg {{
    height: 100%;
}}
.bar-seg.silver {{ background: linear-gradient(90deg, #c41e3a, #e44); }}
.bar-seg.copper {{ background: linear-gradient(90deg, #d4a017, #e6c35c); }}
.bar-seg.labor {{ background: linear-gradient(90deg, #666, #999); }}
.bar-pct {{
    font-size: 8pt;
    color: #888;
    width: 7em;
    flex-shrink: 0;
}}
.bar-legend {{
    display: flex;
    gap: 0.5cm;
    justify-content: center;
    margin-top: 0.2cm;
    font-size: 8pt;
    color: #666;
}}
.leg-dot {{
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 2px;
    margin-right: 3px;
    vertical-align: middle;
}}
.leg-dot.silver {{ background: linear-gradient(135deg, #c41e3a, #e44); }}
.leg-dot.copper {{ background: linear-gradient(135deg, #d4a017, #e6c35c); }}
.leg-dot.labor {{ background: linear-gradient(135deg, #666, #999); }}

/* ===== 可视化：威胁度条形图 ===== */
.threat-chart {{
    margin: 0.3cm 0;
    page-break-inside: avoid;
}}
.t-row {{
    display: flex;
    align-items: center;
    gap: 0.3cm;
    margin: 0.2cm 0;
}}
.t-name {{
    font-size: 9pt;
    color: #555;
    width: 5em;
    text-align: right;
    flex-shrink: 0;
}}
.t-track {{
    flex: 1;
    height: 14px;
    background: #f0f0f0;
    border-radius: 7px;
    overflow: hidden;
}}
.t-bar {{
    height: 100%;
    border-radius: 7px;
}}
.t-bar.t5 {{ background: linear-gradient(90deg, #8B0000, #c41e3a); width: 100%; }}
.t-bar.t3 {{ background: linear-gradient(90deg, #c41e3a, #e66); }}
.t-bar.t2 {{ background: linear-gradient(90deg, #e66, #f88); }}
.t-pct {{
    font-size: 8pt;
    color: #888;
    width: 3em;
    flex-shrink: 0;
}}

/* ===== 可视化：环形图/饼图 ===== */
.donut-wrap, .pie-wrap {{
    display: flex;
    align-items: center;
    gap: 0.8cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}}
.donut, .pie {{
    width: 220px;
    height: 220px;
    border-radius: 50%;
    flex-shrink: 0;
    box-shadow: inset 0 0 0 36px #fff;
}}
.donut-legend, .pie-legend {{
    flex: 1;
}}
.d-leg, .p-leg {{
    font-size: 9pt;
    color: #555;
    margin: 0.15cm 0;
    display: flex;
    align-items: center;
    gap: 0.2cm;
}}
.d-dot, .p-dot {{
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
}}

/* ===== 可视化：GMV柱状图 ===== */
.gmv-chart {{
    display: flex;
    align-items: flex-end;
    gap: 0.4cm;
    height: 120px;
    margin: 0.4cm 0;
    padding: 0.3cm 0.5cm;
    background: #fafafa;
    border-radius: 6px;
    page-break-inside: avoid;
}}
.g-col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
}}
.g-bar {{
    width: 60%;
    background: linear-gradient(180deg, #c41e3a, #8B0000);
    border-radius: 4px 4px 0 0;
    min-height: 8px;
}}
.g-label {{
    font-size: 8pt;
    color: #888;
    margin-top: 0.15cm;
}}
.g-val {{
    font-size: 9pt;
    font-weight: 700;
    color: #c41e3a;
    margin-top: 0.05cm;
}}
.gmv-total {{
    text-align: center;
    font-size: 10pt;
    color: #555;
    margin-top: 0.3cm;
}}
.gmv-total strong {{
    color: #c41e3a;
    font-size: 12pt;
}}

/* ===== 可视化：产品矩阵三列卡片 ===== */
.matrix-three {{
    display: flex;
    gap: 0.4cm;
    margin: 0.4cm 0;
    page-break-inside: avoid;
}}
.m-card {{
    flex: 1;
    background: linear-gradient(135deg, #fafafa, #fff);
    border: 1px solid #eee;
    border-top: 4px solid #d4a017;
    border-radius: 6px;
    padding: 0.4cm;
    text-align: center;
}}
.m-card.m-main {{ border-top-color: #c41e3a; background: linear-gradient(135deg, #fff5f5, #fff); }}
.m-card.m-lux {{ border-top-color: #8B0000; background: linear-gradient(135deg, #f8f0f0, #fff); }}
.m-tier {{
    font-size: 8pt;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.2cm;
}}
.m-name {{
    font-size: 14pt;
    font-weight: 700;
    color: #1a1a1a;
}}
.m-price {{
    font-size: 10pt;
    color: #c41e3a;
    font-weight: 600;
    margin: 0.15cm 0;
}}
.m-scene {{
    font-size: 8.5pt;
    color: #888;
}}

/* ===== 页脚 ===== */
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
{footer_html}
</body>
</html>
'''

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Done: enhanced sample with infographics written.")
