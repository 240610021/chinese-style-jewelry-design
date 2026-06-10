#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺HTML页面解析工具
功能：解析本地保存的淘宝店铺HTML文件，提取商品数据
"""

import os
import re
import json
import csv
from glob import glob
from bs4 import BeautifulSoup
from datetime import datetime

# ============ 配置 ============
HTML_DIR = "."  # HTML文件所在目录（默认当前目录）
OUTPUT_DIR = "output"
SHOP_NAME = "琢匠"

# ============ 核心代码 ============

def parse_product_card(card):
    """解析单个商品卡片"""
    product = {}
    
    try:
        # 提取标题
        title = ""
        # 尝试从a标签的title属性
        a_tag = card.find('a', href=re.compile(r'item\.htm'))
        if a_tag:
            title = a_tag.get('title', '')
            if not title:
                # 尝试从img的alt
                img = a_tag.find('img')
                if img:
                    title = img.get('alt', '')
            if not title:
                # 从文本内容
                title = a_tag.get_text(strip=True)
        
        # 如果还没找到，尝试其他选择器
        if not title:
            for sel in ['.title', '[class*="title"]']:
                el = card.select_one(sel)
                if el:
                    title = el.get_text(strip=True)
                    break
        
        product['title'] = title
        
        # 提取价格 - 找包含¥的元素
        price = ""
        price_el = card.find(string=re.compile(r'¥\s*\d+'))
        if price_el:
            price = price_el.strip()
        else:
            # 尝试找class包含price的元素
            price_el = card.find(class_=re.compile(r'price', re.I))
            if price_el:
                price = price_el.get_text(strip=True)
        
        product['price'] = price
        
        # 提取销量
        sales = ""
        sales_keywords = ['月销', '已售', '人付款', '销量', '售出']
        for keyword in sales_keywords:
            sales_el = card.find(string=re.compile(keyword))
            if sales_el:
                sales = sales_el.strip()
                break
        
        product['sales'] = sales
        
        # 提取链接和ID
        url = ""
        item_id = ""
        if a_tag:
            url = a_tag.get('href', '')
            if url.startswith('//'):
                url = 'https:' + url
            match = re.search(r'id=(\d+)', url)
            if match:
                item_id = match.group(1)
        
        product['item_id'] = item_id
        product['url'] = url
        
        # 提取图片
        img_url = ""
        if a_tag:
            img = a_tag.find('img')
            if img:
                img_url = img.get('src') or img.get('data-src', '')
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
        
        product['img_url'] = img_url
        
        # 提取店铺名
        shop = ""
        shop_el = card.find(class_=re.compile(r'shop', re.I))
        if shop_el:
            shop = shop_el.get_text(strip=True)
        
        product['shop_name'] = shop
        
    except Exception as e:
        pass
    
    return product


def parse_html_file(filepath):
    """解析单个HTML文件"""
    print(f"\n解析: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    products = []
    
    # 策略1：找包含item链接的a标签，然后获取父容器
    item_links = soup.find_all('a', href=re.compile(r'item\.htm'))
    print(f"  找到 {len(item_links)} 个商品链接")
    
    seen_ids = set()
    
    for link in item_links:
        # 向上查找父容器（最多5层）
        parent = link
        for _ in range(5):
            if not parent.parent:
                break
            parent = parent.parent
            
            # 检查是否是商品卡片：包含图片和价格
            img = parent.find('img')
            has_price = bool(parent.find(string=re.compile(r'¥')))
            
            if img and has_price:
                product = parse_product_card(parent)
                
                # 过滤无效数据
                if not product.get('title') or len(product['title']) < 5:
                    continue
                
                # 排除非商品
                exclude = ['消费者保障', '保证金', '收藏店铺', '装修', '品质工厂', '所有分类', '首页']
                if any(k in product['title'] for k in exclude):
                    continue
                
                # 去重
                pid = product.get('item_id') or product.get('title')
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    product['source_file'] = os.path.basename(filepath)
                    product['crawl_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    products.append(product)
                
                break
    
    print(f"  提取到 {len(products)} 个有效商品")
    return products


def analyze_data(products):
    """数据分析"""
    if not products:
        return
    
    print("\n" + "=" * 60)
    print("数据分析")
    print("=" * 60)
    
    # 价格分析
    prices = []
    for p in products:
        price_str = re.sub(r'[^\d.]', '', p.get('price', ''))
        try:
            price = float(price_str)
            if price > 0:
                prices.append(price)
        except:
            pass
    
    if prices:
        print(f"价格统计 ({len(prices)}个有价格):")
        print(f"  最低: ¥{min(prices):.2f}")
        print(f"  最高: ¥{max(prices):.2f}")
        print(f"  平均: ¥{sum(prices)/len(prices):.2f}")
        
        # 价格带
        ranges = {
            '0-50元': 0, '50-100元': 0, '100-200元': 0,
            '200-500元': 0, '500-1000元': 0, '1000元以上': 0,
        }
        for p in prices:
            if p < 50: ranges['0-50元'] += 1
            elif p < 100: ranges['50-100元'] += 1
            elif p < 200: ranges['100-200元'] += 1
            elif p < 500: ranges['200-500元'] += 1
            elif p < 1000: ranges['500-1000元'] += 1
            else: ranges['1000元以上'] += 1
        
        print(f"\n价格带分布:")
        for r, c in ranges.items():
            if c > 0:
                print(f"  {r}: {c} 款 ({c/len(prices)*100:.1f}%)")
    
    # 销量分析
    sales_list = []
    for p in products:
        match = re.search(r'(\d+)', p.get('sales', ''))
        if match:
            sales_list.append(int(match.group(1)))
    
    if sales_list:
        print(f"\n销量统计 ({len(sales_list)}个有销量):")
        print(f"  总销量: {sum(sales_list)} 件")
        print(f"  平均: {sum(sales_list)//len(sales_list)} 件")
        print(f"  最高: {max(sales_list)} 件")


def main():
    print("=" * 60)
    print("淘宝店铺HTML页面解析工具")
    print("=" * 60)
    
    # 查找HTML文件
    html_files = sorted(glob(os.path.join(HTML_DIR, f"{SHOP_NAME}_page_*.html")))
    
    if not html_files:
        print(f"\n未找到HTML文件！")
        print(f"请确保以下文件在当前目录：")
        print(f"  {SHOP_NAME}_page_001.html")
        print(f"  {SHOP_NAME}_page_002.html")
        print(f"  ...")
        return
    
    print(f"\n找到 {len(html_files)} 个HTML文件:")
    for f in html_files:
        print(f"  - {os.path.basename(f)}")
    
    # 解析所有文件
    all_products = []
    for filepath in html_files:
        products = parse_html_file(filepath)
        all_products.extend(products)
    
    print(f"\n{'='*60}")
    print(f"总计提取 {len(all_products)} 个唯一商品")
    print(f"{'='*60}")
    
    if not all_products:
        print("\n未提取到商品数据，请检查HTML文件是否正确")
        return
    
    # 显示前10个
    print("\n前10个商品预览:")
    for i, p in enumerate(all_products[:10]):
        print(f"  {i+1}. {p['title'][:40]}...")
        print(f"     价格: {p.get('price', '未获取')} | 销量: {p.get('sales', '未获取')}")
    
    # 数据分析
    analyze_data(all_products)
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 保存CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    csv_file = os.path.join(OUTPUT_DIR, f"{SHOP_NAME}_parsed_{timestamp}.csv")
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
        writer.writeheader()
        writer.writerows(all_products)
    print(f"\nCSV已保存: {csv_file}")
    
    # 保存JSON
    json_file = os.path.join(OUTPUT_DIR, f"{SHOP_NAME}_parsed_{timestamp}.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    print(f"JSON已保存: {json_file}")
    
    print("\n" + "=" * 60)
    print("全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
