#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from collections import Counter, defaultdict

# Load data
with open(r'g:\Downloads\蔡规划\琢匠产品\parsed_products.json', 'r', encoding='utf-8') as f:
    products = json.load(f)

# ========== 标签定义 ==========

# 文化主题标签
def tag_culture(title):
    t = title.lower()
    tags = []
    # 道系
    if any(k in t for k in ['道系', '山鬼', '太极', '师刀', '天机', '六爻', '铜钱剑', '炼丹炉', '无极炉', '道骨', '卦爻', '紫薇', '五行', '归元']):
        tags.append('道系/玄学')
    # 藏传
    if any(k in t for k in ['藏传', '藏式', '九宫八卦', '金刚杵', '降魔杵', '金刚铃', '大鹏鸟', '多吉', '羯磨杵', '明镜台', '金刚橛']):
        tags.append('藏传/佛教')
    # 三国/古代军事
    if any(k in t for k in ['三国', '赵云', '吕布', '斯巴达', '背嵬军', '锦衣卫', '唐玄甲', '甲胄', '将军令', '维京', '掠夺者', '勇士', '指挥官', '兵人', '武器架']):
        tags.append('古代军事/甲胄')
    # 神兽/瑞兽
    if any(k in t for k in ['貔貅', '饕餮', '青龙', '霸下', '麒麟', '龙', '凤', '狮', '虎', '鱼化龙', '锦鲤', '金蟾', '龟壳', '螭虎']):
        tags.append('神兽/瑞兽')
    # 西游记/神话
    if any(k in t for k in ['悟空', '金箍棒']):
        tags.append('西游/神话')
    # 机械/潮玩
    if any(k in t for k in ['机械', '可动', '潮玩', '蜘蛛', '心脏', '手掌', '黑神话']):
        tags.append('机械/潮玩')
    # 明星/联名
    if any(k in t for k in ['杨幂同款', '明星']):
        tags.append('明星/联名')
    # 佛学符号（不含藏传）
    if any(k in t for k in ['莲花', '宝莲', '福慧', '无相', '金刚心', '护生']):
        if '藏传/佛教' not in tags:
            tags.append('佛学符号')
    if not tags:
        tags.append('通用/其他')
    return tags

# 材质标签
def tag_material(title):
    t = title.lower()
    mats = []
    if 's925银' in t or '银饰' in t or '银饰品' in t or '银手链' in t or '银项链' in t or '银手镯' in t or '银耳' in t or '银配件' in t or '银挂' in t or '银手串' in t or '银镯' in t or '银链' in t or '银绳' in t or '银圈' in t or '银垫' in t or '银卡' in t:
        mats.append('S925银')
    if any(k in t for k in ['黄铜', '铜饰品', '铜手把', '铜摆件', '铜器', '铜工艺', '铜装饰', '铜手办', '铜钥匙', '铜绳', '乌铜']):
        mats.append('黄铜/紫铜')
    if '全银' in t or '全铜' in t:
        if '全银' in t:
            mats.append('全银定制')
        if '全铜' in t:
            mats.append('全铜')
    if '桃木' in t:
        mats.append('桃木')
    if '黑曜石' in t or '水晶' in t:
        mats.append('黑曜石/水晶')
    if '椰蒂' in t:
        mats.append('椰蒂菩提')
    if '菩提' in t or '猴头' in t or '核桃' in t or '金刚' in t:
        mats.append('菩提/文玩材质')
    if '青铜' in t:
        mats.append('青铜')
    if '包芯棉绳' in t or '编织绳' in t or '手绳' in t or '挂绳' in t or '红手绳' in t:
        mats.append('绳线/编织')
    if not mats:
        mats.append('未标注/其他')
    return mats

# 功能/结构标签
def tag_function(title):
    t = title.lower()
    funcs = []
    # 可玩性结构
    if any(k in t for k in ['可动', '磁吸', '万向轴', '拼装', 'diy', '组装']):
        funcs.append('可动/磁吸/DIY')
    # 解压
    if '解压' in t:
        funcs.append('解压')
    # 定制
    if '定制' in t:
        funcs.append('定制')
    # 合集/套装
    if '合集' in t or '集合' in t or '全套' in t:
        funcs.append('合集/套装')
    # 明星同款
    if '杨幂同款' in t:
        funcs.append('明星同款')
    # 游戏IP
    if '黑神话' in t:
        funcs.append('游戏IP')
    if not funcs:
        funcs.append('常规')
    return funcs

# 具体符号元素提取
def tag_symbols(title):
    t = title
    symbols = []
    symbol_list = ['貔貅', '饕餮', '青龙', '霸下', '麒麟', '龙', '凤', '狮', '醒狮', '虎', '螭虎', '锦鲤', '金蟾', '龟壳', '鱼化龙',
                   '山鬼', '太极', '师刀', '天机', '六爻', '铜钱剑', '炼丹炉', '无极炉', '道骨', '卦爻', '紫薇', '八卦',
                   '金刚杵', '降魔杵', '金刚铃', '大鹏鸟', '多吉', '羯磨杵', '金刚橛', '明镜台', '九宫',
                   '赵云', '吕布', '斯巴达', '背嵬军', '锦衣卫', '唐玄甲', '甲胄', '将军令', '维京', '兵人',
                   '悟空', '金箍棒', '莲花', '宝莲', '福慧', '无相', '金刚心', '护生',
                   '机械蜘蛛', '机械心脏', '黑神话', '钟馗']
    for s in symbol_list:
        if s in t:
            symbols.append(s)
    return symbols

# ========== 执行标签化 ==========
for p in products:
    t = p['title']
    p['culture_tags'] = tag_culture(t)
    p['material_tags'] = tag_material(t)
    p['function_tags'] = tag_function(t)
    p['symbols'] = tag_symbols(t)

# ========== 统计分析 ==========

# 1. 文化主题分布
culture_counter = Counter()
for p in products:
    for tag in p['culture_tags']:
        culture_counter[tag] += 1

# 2. 材质分布
material_counter = Counter()
for p in products:
    for tag in p['material_tags']:
        material_counter[tag] += 1

# 3. 功能/结构分布
function_counter = Counter()
for p in products:
    for tag in p['function_tags']:
        function_counter[tag] += 1

# 4. 销量 × 文化主题
culture_sales = defaultdict(list)
for p in products:
    if p['sales']:
        for tag in p['culture_tags']:
            culture_sales[tag].append(p['sales'])

# 5. 销量 × 材质
material_sales = defaultdict(list)
for p in products:
    if p['sales']:
        for tag in p['material_tags']:
            material_sales[tag].append(p['sales'])

# 6. 销量 × 功能
function_sales = defaultdict(list)
for p in products:
    if p['sales']:
        for tag in p['function_tags']:
            function_sales[tag].append(p['sales'])

# 7. 符号元素销量排名
symbol_sales = defaultdict(list)
for p in products:
    if p['sales']:
        for sym in p['symbols']:
            symbol_sales[sym].append(p['sales'])

# 8. 系列化分析（从标题提取系列关键词）
series_keywords = ['天机', '山鬼', '太极', '师刀', '唐玄甲', '悟空', '如意纹', '盘龙', '龙鳞', '龙爪', '龙纹',
                   '金刚', '貔貅', '饕餮', '霸下', '九宫', '五路财神', '护生', '福慧', '无相', '道骨',
                   '吕布', '赵云', '锦衣卫', '背嵬军', '斯巴达', '维京', '大玩家', '铜钱剑', '黑神话']
series_counter = Counter()
series_sales = defaultdict(list)
for p in products:
    t = p['title']
    found_series = []
    for kw in series_keywords:
        if kw in t:
            found_series.append(kw)
    for s in found_series:
        series_counter[s] += 1
        if p['sales']:
            series_sales[s].append(p['sales'])

# ========== 生成报告 ==========
report = []
report.append("=" * 80)
report.append("琢匠产品深度分析报告 —— 特点、差异化与销量关联")
report.append("=" * 80)
report.append(f"\n分析样本：{len(products)} 款商品")
report.append(f"有销量数据：{sum(1 for p in products if p['sales'])} 款")
report.append("")

# 一、文化主题分析
report.append("=" * 80)
report.append("一、文化主题分布与销量表现")
report.append("=" * 80)
report.append("\n【文化主题 SKU 分布】")
for tag, cnt in culture_counter.most_common():
    report.append(f"  {tag}: {cnt} 款 ({cnt/len(products)*100:.1f}%)")

report.append("\n【文化主题 × 销量表现】（有销量的款）")
for tag in culture_counter.keys():
    if tag in culture_sales and culture_sales[tag]:
        avg = sum(culture_sales[tag]) / len(culture_sales[tag])
        total = sum(culture_sales[tag])
        mx = max(culture_sales[tag])
        report.append(f"  {tag}: {len(culture_sales[tag])}款有销量 | 总销量 {total} | 均值 {avg:.0f} | 最高 {mx}")

# 二、材质分析
report.append("\n" + "=" * 80)
report.append("二、材质分布与销量表现")
report.append("=" * 80)
report.append("\n【材质 SKU 分布】")
for tag, cnt in material_counter.most_common():
    report.append(f"  {tag}: {cnt} 款 ({cnt/len(products)*100:.1f}%)")

report.append("\n【材质 × 销量表现】")
for tag in material_counter.keys():
    if tag in material_sales and material_sales[tag]:
        avg = sum(material_sales[tag]) / len(material_sales[tag])
        total = sum(material_sales[tag])
        mx = max(material_sales[tag])
        report.append(f"  {tag}: {len(material_sales[tag])}款有销量 | 总销量 {total} | 均值 {avg:.0f} | 最高 {mx}")

# 三、功能/差异化结构
report.append("\n" + "=" * 80)
report.append("三、功能结构与差异化特征")
report.append("=" * 80)
report.append("\n【功能标签 SKU 分布】")
for tag, cnt in function_counter.most_common():
    report.append(f"  {tag}: {cnt} 款 ({cnt/len(products)*100:.1f}%)")

report.append("\n【差异化功能 × 销量表现】")
for tag in function_counter.keys():
    if tag in function_sales and function_sales[tag]:
        avg = sum(function_sales[tag]) / len(function_sales[tag])
        total = sum(function_sales[tag])
        mx = max(function_sales[tag])
        report.append(f"  {tag}: {len(function_sales[tag])}款有销量 | 总销量 {total} | 均值 {avg:.0f} | 最高 {mx}")

# 四、符号元素销量排名
report.append("\n" + "=" * 80)
report.append("四、具体文化符号销量排名")
report.append("=" * 80)
symbol_avg = []
for sym, sales in symbol_sales.items():
    if len(sales) >= 2:  # 至少2款才统计
        avg = sum(sales) / len(sales)
        symbol_avg.append((sym, len(sales), sum(sales), avg, max(sales)))
symbol_avg.sort(key=lambda x: x[3], reverse=True)
report.append("\n【按平均销量排序】（仅统计≥2款的符号）")
for sym, cnt, total, avg, mx in symbol_avg[:25]:
    report.append(f"  {sym}: {cnt}款 | 总销{total} | 均值{avg:.0f} | 最高{mx}")

# 五、系列化分析
report.append("\n" + "=" * 80)
report.append("五、系列化产品线分析")
report.append("=" * 80)
series_avg = []
for s, cnt in series_counter.most_common():
    if s in series_sales and series_sales[s]:
        avg = sum(series_sales[s]) / len(series_sales[s])
        series_avg.append((s, cnt, len(series_sales[s]), sum(series_sales[s]), avg, max(series_sales[s])))
series_avg.sort(key=lambda x: x[4], reverse=True)
report.append("\n【系列名称 | SKU数 | 有销量款 | 总销量 | 均值 | 最高】")
for s, cnt, sales_cnt, total, avg, mx in series_avg[:30]:
    report.append(f"  {s}: {cnt}款 | {sales_cnt}款有销 | 总销{total} | 均值{avg:.0f} | 最高{mx}")

# 六、爆款特征总结
report.append("\n" + "=" * 80)
report.append("六、TOP 爆款特征拆解")
report.append("=" * 80)
top_products = sorted([p for p in products if p['sales']], key=lambda x: x['sales'], reverse=True)[:15]
for i, p in enumerate(top_products, 1):
    report.append(f"\n{i}. {p['title'][:55]}")
    report.append(f"   销量: {p['sales']} | 品类: {p['category']}")
    report.append(f"   文化: {', '.join(p['culture_tags'])}")
    report.append(f"   材质: {', '.join(p['material_tags'])}")
    report.append(f"   功能: {', '.join(p['function_tags'])}")
    report.append(f"   符号: {', '.join(p['symbols'])}")

# 七、命名规律分析
report.append("\n" + "=" * 80)
report.append("七、产品命名规律与话术拆解")
report.append("=" * 80)
name_patterns = Counter()
for p in products:
    t = p['title']
    if '丨' in t or '|' in t:
        name_patterns['使用「丨」分隔品牌与产品名'] += 1
    if '小众' in t:
        name_patterns['强调「小众」'] += 1
    if '原创' in t:
        name_patterns['强调「原创」'] += 1
    if '国风' in t:
        name_patterns['强调「国风」'] += 1
    if 's925' in t.lower() or '925银' in t:
        name_patterns['标注「S925银」材质'] += 1
    if 'diy' in t.lower():
        name_patterns['标注「DIY」可玩性'] += 1
    if '解压' in t:
        name_patterns['标注「解压」场景'] += 1
    if '情侣' in t:
        name_patterns['标注「情侣」人群'] += 1
    if '男士' in t:
        name_patterns['标注「男士」人群'] += 1
    if '礼物' in t or '礼品' in t:
        name_patterns['标注「礼物/礼品」场景'] += 1
    if '新款' in t or '爆款' in t:
        name_patterns['标注「新款/爆款」'] += 1
    if '手工' in t:
        name_patterns['标注「手工」工艺'] += 1

report.append("\n【标题高频话术】")
for pat, cnt in name_patterns.most_common():
    report.append(f"  {pat}: {cnt} 款 ({cnt/len(products)*100:.1f}%)")

# 八、失败款分析
report.append("\n" + "=" * 80)
report.append("八、低销量款（≤50件）深度分析")
report.append("=" * 80)
low_sales = [p for p in products if p['sales'] and p['sales'] <= 50]
report.append(f"\n共 {len(low_sales)} 款低销量商品：\n")
for p in low_sales:
    report.append(f"- {p['title'][:60]}")
    report.append(f"  销量: {p['sales']} | 品类: {p['category']}")
    report.append(f"  文化: {', '.join(p['culture_tags'])} | 材质: {', '.join(p['material_tags'])}")
    report.append(f"  功能: {', '.join(p['function_tags'])}")
    report.append("")

# 九、核心结论
report.append("=" * 80)
report.append("九、核心结论与差异化总结")
report.append("=" * 80)
report.append("""
【琢匠的五大差异化壁垒】

1. 文化符号的「硬核化」
   - 不做泛泛的「国风」，而是深挖道系（山鬼/太极/师刀）、藏传（九宫八卦/金刚杵）、
     古代军事（甲胄/兵人）三大硬核文化赛道
   - 每个符号都有明确的宗教/历史出处，吸引高忠诚度圈层

2. 材质的「金属信仰」
   - S925银（占比最高）和黄铜/紫铜双主线，形成「可盘可养」的文玩属性
   - 与木质、树脂竞品形成材质壁垒

3. 结构的「可玩性」
   - 磁吸金属人仔（赵云/吕布/斯巴达）、可动机械蜘蛛、万向轴三通
   - 从「静态饰品」升级为「可盘玩物件」，提升用户停留时长和社交传播

4. 系列的「矩阵化」
   - 同一文化符号做多 SKU 延伸：山鬼→手镯/三通/花钱/吊坠；悟空→三通/弟子珠/炼心隔珠
   - 降低研发成本，提升用户客单价和复购率

5. 命名的「圈层暗号」
   - 标题高频使用「小众」「原创」「国风」「道系」「s925银」
   - 「丨」分隔符形成品牌视觉识别
   - 人群标签（男士/情侣）和场景标签（解压/礼物/DIY）精准命中搜索关键词

【最受欢迎的产品公式】
销量爆款 = 硬核文化符号（道系/神兽/军事） + S925银材质 + 可玩/实用结构 + 男性向场景

【需要规避的方向】
- 无极炉系列（手链+项链）双双滞销，说明同一文化概念内部 SKU 过多会导致流量稀释
- 定制款（天机剑匣/机械心脏）销量个位数，只能作为品牌调性，不能指望走量
- 藏传细分（大鹏鸟计数器）受众过窄，天然长尾
""")

report_text = "\n".join(report)
print(report_text)

with open(r'g:\Downloads\蔡规划\琢匠产品\深度分析报告.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n\n深度分析报告已保存至: g:\\Downloads\\蔡规划\\琢匠产品\\深度分析报告.txt")
