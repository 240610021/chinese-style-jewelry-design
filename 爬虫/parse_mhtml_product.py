#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝商品详情页 MHTML 解析工具
功能：解析保存的淘宝商品详情页.mhtml文件，提取商品数据
"""

import os
import re
import json
import csv
from datetime import datetime
from glob import glob

# 安装依赖：pip install beautifulsoup4
from bs4 import BeautifulSoup


def parse_mhtml_file(filepath):
    """解析MHTML文件，提取HTML内容"""
    print(f"\n解析: {os.path.basename(filepath)}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # MHTML格式处理：提取HTML部分
    # 查找Content-Type: text/html部分
    html_content = ""
    
    # 尝试提取HTML
    if '<!DOCTYPE html>' in content or '<html' in content:
        # 已经是纯HTML或包含HTML
        html_start = content.find('<!DOCTYPE html>')
        if html_start == -1:
            html_start = content.find('<html')
        if html_start != -1:
            html_content = content[html_start:]
    else:
        # 标准的MHTML格式，需要解码
        # 查找base64编码的HTML部分
        print("  检测到标准MHTML格式，尝试解码...")
        # 简单处理：找Content-Transfer-Encoding: base64后面的内容
        parts = content.split('Content-Type: text/html')
        if len(parts) > 1:
            html_part = parts[1]
            # 找base64内容
            if 'base64' in html_part:
                import base64
                # 提取base64编码的文本
                lines = html_part.split('\n')
                base64_text = ''
                started = False
                for line in lines:
                    if started and line.strip() and not line.startswith('------'):
                        base64_text += line.strip()
                    if 'base64' in line:
                        started = True
                if base64_text:
                    try:
                        html_content = base64.b64decode(base64_text).decode('utf-8', errors='ignore')
                    except:
                        pass
    
    if not html_content:
        print("  ⚠️ 无法提取HTML内容，尝试直接解析整个文件...")
        html_content = content
    
    return html_content


def extract_product_data(html_content):
    """从HTML中提取商品数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    product = {
        'title': '',
        'price': '',
        'promo_price': '',
        'original_price': '',
        'sales': '',
        'reviews': '',
        'shop_name': '',
        'shop_url': '',
        'item_id': '',
        'url': '',
        'category': '',
        'params': {},
        'sku_list': [],
        'img_urls': [],
        'crawl_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 1. 提取标题
    # 方法1：从title标签
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        # 淘宝标题通常是 "商品名 - 淘宝网"
        if ' - ' in title_text:
            product['title'] = title_text.split(' - ')[0]
        else:
            product['title'] = title_text
    
    # 方法2：从meta
    if not product['title']:
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            product['title'] = meta_title.get('content', '')
    
    # 2. 提取价格
    # 找包含¥的元素
    price_patterns = [
        r'¥\s*(\d+\.?\d*)',
        r'价格[：:]\s*(\d+\.?\d*)',
        r'(\d+\.\d{2})',
    ]
    
    # 尝试从文本中找价格
    for pattern in price_patterns:
        matches = re.findall(pattern, html_content)
        if matches:
            prices = [float(m) for m in matches if float(m) > 10]  # 过滤掉太小的数字
            if prices:
                product['price'] = f'¥{min(prices):.2f}'
                if len(prices) > 1:
                    product['original_price'] = f'¥{max(prices):.2f}'
                break
    
    # 3. 提取销量
    sales_patterns = [
        r'月销\s*(\d+)',
        r'已售\s*(\d+)',
        r'(\d+)\s*人付款',
        r'销量[：:]\s*(\d+)',
        r'累计评论\s*(\d+)',
    ]
    
    for pattern in sales_patterns:
        match = re.search(pattern, html_content)
        if match:
            product['sales'] = match.group(0)
            break
    
    # 4. 提取评价数
    review_patterns = [
        r'评价\s*(\d+)',
        r'累计评论\s*(\d+)',
        r'(\d+)\s*条评价',
    ]
    
    for pattern in review_patterns:
        match = re.search(pattern, html_content)
        if match:
            product['reviews'] = match.group(0)
            break
    
    # 5. 提取店铺名
    shop_patterns = [
        r'店铺[：:]\s*([^<\n]+)',
        r'掌柜[：:]\s*([^<\n]+)',
    ]
    
    for pattern in shop_patterns:
        match = re.search(pattern, html_content)
        if match:
            product['shop_name'] = match.group(1).strip()
            break
    
    # 6. 提取商品ID
    id_match = re.search(r'id=(\d+)', html_content)
    if id_match:
        product['item_id'] = id_match.group(1)
    
    # 7. 提取商品参数
    # 找参数表格或列表
    param_sections = soup.find_all(string=re.compile(r'商品参数|产品参数|规格参数'))
    for section in param_sections:
        parent = section.parent
        for _ in range(5):
            if not parent:
                break
            # 找dl/dt/dd结构
            dts = parent.find_all('dt')
            dds = parent.find_all('dd')
            if dts and dds and len(dts) == len(dds):
                for dt, dd in zip(dts, dds):
                    key = dt.get_text(strip=True)
                    value = dd.get_text(strip=True)
                    if key and value:
                        product['params'][key] = value
                break
            parent = parent.parent
    
    # 8. 提取SKU
    sku_patterns = [
        r'data-sku[^>]*>([^<]+)<',
        r'SKU[：:]\s*([^<\n]+)',
    ]
    
    # 9. 提取图片URL
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src') or img.get('data-src')
        if src and ('taobaocdn' in src or 'alicdn' in src):
            if src.startswith('//'):
                src = 'https:' + src
            product['img_urls'].append(src)
    
    # 去重图片
    product['img_urls'] = list(set(product['img_urls']))[:10]  # 最多保留10张
    
    return product


def print_product_info(product):
    """打印商品信息"""
    print("\n" + "=" * 60)
    print("商品信息")
    print("=" * 60)
    
    print(f"标题: {product['title']}")
    print(f"价格: {product['price']}")
    if product['promo_price']:
        print(f"促销价: {product['promo_price']}")
    if product['original_price']:
        print(f"原价: {product['original_price']}")
    print(f"销量: {product['sales']}")
    print(f"评价: {product['reviews']}")
    print(f"店铺: {product['shop_name']}")
    print(f"商品ID: {product['item_id']}")
    
    if product['params']:
        print(f"\n商品参数:")
        for k, v in product['params'].items():
            print(f"  {k}: {v}")
    
    if product['img_urls']:
        print(f"\n图片URL ({len(product['img_urls'])}张):")
        for i, url in enumerate(product['img_urls'][:5], 1):
            print(f"  {i}. {url[:80]}...")


def main():
    print("=" * 60)
    print("淘宝商品详情页 MHTML 解析工具")
    print("=" * 60)
    
    # 查找MHTML文件
    mhtml_files = glob("*.mhtml") + glob("*.html")
    
    # 过滤掉已处理的文件
    mhtml_files = [f for f in mhtml_files if not f.startswith('parsed_')]
    
    if not mhtml_files:
        print("\n未找到MHTML或HTML文件！")
        print("请确保文件在当前目录")
        return
    
    print(f"\n找到 {len(mhtml_files)} 个文件:")
    for f in mhtml_files:
        print(f"  - {f}")
    
    all_products = []
    
    for filepath in mhtml_files:
        try:
            html_content = parse_mhtml_file(filepath)
            product = extract_product_data(html_content)
            
            if product['title']:
                print_product_info(product)
                all_products.append(product)
            else:
                print("  ⚠️ 未能提取到商品标题，可能格式不支持")
        
        except Exception as e:
            print(f"  ❌ 解析失败: {e}")
    
    # 保存结果
    if all_products:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_file = f"parsed_products_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        print(f"\n✅ JSON已保存: {json_file}")
        
        # CSV
        csv_file = f"parsed_products_{timestamp}.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'price', 'sales', 'reviews', 'shop_name', 'item_id', 'url', 'crawl_time'])
            writer.writeheader()
            for p in all_products:
                writer.writerow({
                    'title': p['title'],
                    'price': p['price'],
                    'sales': p['sales'],
                    'reviews': p['reviews'],
                    'shop_name': p['shop_name'],
                    'item_id': p['item_id'],
                    'url': p['url'],
                    'crawl_time': p['crawl_time']
                })
        print(f"✅ CSV已保存: {csv_file}")
    
    print("\n" + "=" * 60)
    print("全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
