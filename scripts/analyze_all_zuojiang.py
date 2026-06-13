#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import csv
import quopri
from glob import glob
from bs4 import BeautifulSoup
from collections import Counter

TARGET_DIR = r"g:\Downloads\蔡规划\琢匠产品"

def decode_qp(text):
    try:
        return quopri.decodestring(text.encode()).decode('utf-8', errors='ignore')
    except:
        return text

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    html_start = raw.find('<!DOCTYPE html>')
    if html_start == -1:
        html_start = raw.find('<html')
    if html_start == -1:
        html_start = 0
    html_raw = raw[html_start:]
    html = decode_qp(html_raw)

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')

    # Title
    title = ''
    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        if ' - ' in t:
            title = t.split(' - ')[0]
        else:
            title = t

    # Price from visible text
    prices = []
    for line in text.splitlines():
        for m in re.finditer(r'¥\s*(\d+\.?\d*)', line):
            try:
                pv = float(m.group(1))
                if 1 <= pv <= 999999:
                    prices.append(pv)
            except:
                pass
    price = min(prices) if prices else None

    # Sales
    sales = None
    for line in text.splitlines():
        line = line.strip()
        m = re.search(r'(?:月销|已售|销量)[\s:：]*(\d+)', line)
        if m:
            try:
                sales = int(m.group(1))
                break
            except:
                pass
        m = re.search(r'(\d+)\s*人付款', line)
        if m:
            try:
                sales = int(m.group(1))
                break
            except:
                pass

    # Reviews
    reviews = None
    for line in text.splitlines():
        line = line.strip()
        m = re.search(r'(?:累计评论|评价)[\s:：]*(\d+)', line)
        if m:
            try:
                reviews = int(m.group(1))
                break
            except:
                pass
        m = re.search(r'(\d+)\s*条评价', line)
        if m:
            try:
                reviews = int(m.group(1))
                break
            except:
                pass

    # Shop
    shop = ''
    for line in text.splitlines():
        if '店铺' in line and ('：' in line or ':' in line):
            parts = re.split(r'[:：]', line, 1)
            if len(parts) == 2:
                shop = parts[1].strip()
                break

    # Item ID
    item_id = ''
    m = re.search(r'[?&]id=(\d+)', raw)
    if m:
        item_id = m.group(1)

    return {
        'filename': os.path.basename(filepath),
        'title': title,
        'price': price,
        'sales': sales,
        'reviews': reviews,
        'shop': shop,
        'item_id': item_id,
    }

def classify_product(title):
    t = title.lower()
    if any(k in t for k in ['摆件', '手办', '桌面', '客厅', '玄关', '书房', '茶宠', '茶室', '办公室', '装饰品']):
        return '摆件/手办'
    if any(k in t for k in ['手串', '隔珠', '隔片', '三通', '背云', '链接扣', '卡环', '跑环', '配珠', '散珠', '合集', '弟子珠', '流苏', '线束', '侧挂', '小提溜', '隔环', '垫片', '腰珠', '顶珠']):
        return '手串配件'
    if any(k in t for k in ['吊坠', '项链', '挂坠', '挂件', '绳链', '挂饰', '单坠']):
        return '吊坠/挂件'
    if any(k in t for k in ['手链', '手镯', '手绳', '手持', '流珠', '念珠']):
        return '手链/手镯'
    if any(k in t for k in ['耳环', '耳夹', '耳钉', '耳饰']):
        return '耳饰'
    if any(k in t for k in ['钥匙扣', '钥匙链', '钥匙圈']):
        return '钥匙扣'
    if any(k in t for k in ['手把件', '解压', 'edc']):
        return '手把件/EDC'
    return '其他'

def main():
    os.chdir(TARGET_DIR)
    files = glob('*.mhtml') + glob('*.html')
    files = [f for f in files if not f.startswith('parsed_') and not f.startswith('analyze')]
    products = []
    for fp in files:
        try:
            data = parse_file(fp)
            data['category'] = classify_product(data['title'])
            products.append(data)
        except Exception as e:
            print(f'Error: {fp} -> {e}')

    # Stats
    total = len(products)
    with_price = sum(1 for p in products if p['price'])
    with_sales = sum(1 for p in products if p['sales'])
    with_reviews = sum(1 for p in products if p['reviews'])

    sales_list = [p['sales'] for p in products if p['sales']]
    price_list = [p['price'] for p in products if p['price']]
    review_list = [p['reviews'] for p in products if p['reviews']]

    cat_counter = Counter(p['category'] for p in products)

    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("琢匠店铺 MHTML 样本分析报告（全量）")
    report_lines.append("=" * 60)
    report_lines.append(f"样本总数: {total} 个商品页面")
    report_lines.append(f"成功提取价格: {with_price} 个")
    report_lines.append(f"成功提取销量: {with_sales} 个")
    report_lines.append(f"成功提取评价: {with_reviews} 个")
    report_lines.append("")

    if price_list:
        report_lines.append(f"价格统计 ({len(price_list)}个):")
        report_lines.append(f"  最低: ¥{min(price_list):.2f}")
        report_lines.append(f"  最高: ¥{max(price_list):.2f}")
        report_lines.append(f"  平均: ¥{sum(price_list)/len(price_list):.2f}")
        report_lines.append("")

    if sales_list:
        report_lines.append(f"销量统计 ({len(sales_list)}个):")
        report_lines.append(f"  总销量: {sum(sales_list)} 件")
        report_lines.append(f"  平均: {sum(sales_list)//len(sales_list)} 件/款")
        report_lines.append(f"  最高: {max(sales_list)} 件")
        report_lines.append(f"  最低: {min(sales_list)} 件")
        report_lines.append("")

    if review_list:
        report_lines.append(f"评价统计 ({len(review_list)}个):")
        report_lines.append(f"  总评价: {sum(review_list)} 条")
        report_lines.append(f"  平均: {sum(review_list)//len(review_list)} 条/款")
        report_lines.append("")

    report_lines.append("品类分布:")
    for cat, cnt in cat_counter.most_common():
        report_lines.append(f"  {cat}: {cnt} 款 ({cnt/total*100:.1f}%)")
    report_lines.append("")

    report_lines.append("=" * 60)
    report_lines.append("各商品详情")
    report_lines.append("=" * 60)
    for p in products:
        report_lines.append(f"\n商品: {p['title'][:80]}")
        report_lines.append(f"  品类: {p['category']}")
        report_lines.append(f"  价格: {'¥'+str(p['price']) if p['price'] else '未提取'}")
        report_lines.append(f"  销量: {p['sales'] if p['sales'] else '未提取'}")
        report_lines.append(f"  评价: {p['reviews'] if p['reviews'] else '未提取'}")
        report_lines.append(f"  店铺: {p['shop'] if p['shop'] else '未提取'}")
        report_lines.append(f"  商品ID: {p['item_id']}")

    report_text = "\n".join(report_lines)

    with open('parsed_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    with open('parsed_products.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','title','category','price','sales','reviews','shop','item_id'])
        writer.writeheader()
        for p in products:
            writer.writerow(p)

    with open('parsed_report.txt', 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print('\nSaved parsed_products.json, parsed_products.csv, parsed_report.txt')

if __name__ == '__main__':
    main()
