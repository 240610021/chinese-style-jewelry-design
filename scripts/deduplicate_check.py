#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import Counter

# Load both datasets
with open(r'g:\Downloads\蔡规划\新建文件夹\parsed_products.json', 'r', encoding='utf-8') as f:
    old_products = json.load(f)

with open(r'g:\Downloads\蔡规划\琢匠产品\parsed_products.json', 'r', encoding='utf-8') as f:
    new_products = json.load(f)

print("=" * 70)
print("重复产品排查报告")
print("=" * 70)

# 1. 按 item_id 检查新样本内部重复
print("\n【一、新样本内部重复（按商品ID）】")
id_counter = Counter(p['item_id'] for p in new_products)
duplicates = {k: v for k, v in id_counter.items() if v > 1}
if duplicates:
    for item_id, count in duplicates.items():
        titles = [p['title'] for p in new_products if p['item_id'] == item_id]
        print(f"  商品ID {item_id}: 出现 {count} 次")
        for t in titles:
            print(f"    - {t[:70]}")
else:
    print("  新样本内部无重复商品ID")

# 2. 新旧样本交叉重复
print("\n【二、新旧样本交叉重复】")
old_ids = {p['item_id'] for p in old_products}
new_ids = {p['item_id'] for p in new_products}
cross_dup = old_ids & new_ids
if cross_dup:
    print(f"  发现 {len(cross_dup)} 款商品同时存在于两个样本中：")
    for item_id in cross_dup:
        old_t = [p['title'] for p in old_products if p['item_id'] == item_id][0]
        new_t = [p['title'] for p in new_products if p['item_id'] == item_id][0]
        print(f"  商品ID {item_id}")
        print(f"    旧样本: {old_t[:60]}")
        print(f"    新样本: {new_t[:60]}")
else:
    print("  新旧样本无交叉重复")

# 3. 按标题相似度检查（去除店铺名后的核心标题重复）
print("\n【三、标题核心内容重复排查】")
def core_title(title):
    # Remove 店铺名和平台后缀
    t = title.replace('琢匠', '').replace('-淘宝网', '').replace('丨', '|')
    # Keep only the part before |
    if '|' in t:
        t = t.split('|')[0]
    return t.strip()[:20]

core_titles = [core_title(p['title']) for p in new_products]
core_counter = Counter(core_titles)
title_dups = {k: v for k, v in core_counter.items() if v > 1 and k}
if title_dups:
    print("  核心标题重复（可能是同一产品的不同变体页面）：")
    for ct, count in title_dups.items():
        print(f"    '{ct}': {count} 款")
        for p in new_products:
            if core_title(p['title']) == ct:
                print(f"      - {p['title'][:70]} (ID:{p['item_id']})")
else:
    print("  无核心标题重复")

# 4. "合集"类产品分析（一个页面包含多个SKU，会稀释单品数据）
print("\n【四、合集/套装类产品清单】")
heji = [p for p in new_products if '合集' in p['title'] or '集合' in p['title'] or '全套' in p['title']]
print(f"  共发现 {len(heji)} 款合集类产品：")
for p in heji:
    print(f"    - {p['title'][:70]} (销量:{p['sales']})")

# 5. 系列内产品统计（同一概念多款产品，非重复但需说明）
print("\n【五、高密度系列（同一概念≥3款）】")
series_keywords = {
    '天机': ['天机'],
    '山鬼': ['山鬼'],
    '悟空': ['悟空'],
    '龙': ['龙三通', '龙摆件', '盘龙', '龙鳞', '龙爪', '龙纹'],
    '貔貅': ['貔貅'],
    '金刚': ['金刚杵', '降魔杵', '金刚铃', '金刚心', '金刚橛'],
    '师刀': ['师刀'],
    '太极': ['太极'],
    '饕餮': ['饕餮'],
    '唐玄甲': ['唐玄甲'],
    '甲胄': ['甲胄'],
    '锦鲤': ['锦鲤'],
    '葫芦': ['葫芦', '剑葫'],
    '霸下': ['霸下'],
}
for series, kws in series_keywords.items():
    matches = []
    for p in new_products:
        if any(kw in p['title'] for kw in kws):
            matches.append(p)
    if len(matches) >= 3:
        print(f"\n  【{series}系列】共 {len(matches)} 款：")
        for p in matches:
            print(f"    - {p['title'][:65]} (销量:{p['sales']})")

# 6. 生成去重后的统计
print("\n" + "=" * 70)
print("【六、去重后样本量修正】")
print("=" * 70)
unique_ids = len(set(p['item_id'] for p in new_products))
print(f"新样本总商品数: {len(new_products)}")
print(f"去重后商品数: {unique_ids}")
print(f"重复/冗余数量: {len(new_products) - unique_ids}")
