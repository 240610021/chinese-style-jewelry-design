#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝商品详情页 MHTML 批量解析工具
功能：批量解析当前目录下所有.mhtml/.html文件，提取商品数据并汇总
"""

import os
import re
import json
import csv
from datetime import datetime
from glob import glob

from bs4 import BeautifulSoup


def extract_html_from_mhtml(content):
    """从MHTML内容中提取HTML"""
    # 方法1：直接找HTML标签
    html_start = content.find('<!DOCTYPE html>')
    if html_start == -1:
        html_start = content.find('<html')
    
    if html_start != -1:
        return content[html_start:]
    
    # 方法2：MHTML base64解码
    if 'Content-Type: text/html' in content and 'base64' in content:
        import base64
        parts = content.split('Content-Type: text/html')
        if len(parts) > 1:
            html_part = parts[1]
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
                    return base64.b64decode(base64_text).decode('utf-8', errors='ignore')
                except:
                    pass
    
    return content


def parse_price(text):
    """从文本中提取价格"""
    # 找 ¥xxx.xx 或 xxx.xx 元
    patterns = [
        r'¥\s*(\d+\.\d{2})',
        r'(\d+\.\d{2})\s*元',
        r'价格[：:]\s*(\d+\.?\d*)',
        r'现价[：:]\s*(\d+\.?\d*)',
    ]
    
    prices = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for m in matches:
            try:
                price = float(m)
                if 10 < price < 100000:  # 合理价格范围
                    prices.append(price)
            except:
                continue
    
    if prices:
        return min(prices), max(prices) if len(prices) > 1 else None
    return None, None


def extract_product_data(html_content, filename):
    """从HTML中提取商品数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    
    product = {
        'filename': filename,
        'title': '',
        'price': '',
        'original_price': '',
        'sales_count': '',
        'reviews_count': '',
        'shop_name': '',
        'item_id': '',
        'category': '',
        'params': {},
        'crawl_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 1. 提取标题
    # 从title标签
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.get_text(strip=True)
        if ' - ' in title_text:
            product['title'] = title_text.split(' - ')[0]
        else:
            product['title'] = title_text
    
    # 从meta
    if not product['title']:
        meta = soup.find('meta', property='og:title')
        if meta:
            product['title'] = meta.get('content', '')
    
    # 2. 提取价格
    min_price, max_price = parse_price(text)
    if min_price:
        product['price'] = f'¥{min_price:.2f}'
    if max_price and max_price != min_price:
        product['original_price'] = f'¥{max_price:.2f}'
    
    # 3. 提取销量（数字）
    sales_patterns = [
        r'月销\s*(\d+)',
        r'已售\s*(\d+)',
        r'(\d+)\s*人付款',
        r'销量[：:]\s*(\d+)',
    ]
    
    for pattern in sales_patterns:
        match = re.search(pattern, text)
        if match:
            product['sales_count'] = match.group(1)
            break
    
    # 4. 提取评价数
    review_patterns = [
        r'累计评论\s*(\d+)',
        r'(\d+)\s*条评价',
        r'评价\s*(\d+)',
    ]
    
    for pattern in review_patterns:
        match = re.search(pattern, text)
        if match:
            product['reviews_count'] = match.group(1)
            break
    
    # 5. 提取店铺名
    shop_patterns = [
        r'店铺[：:]\s*([^\n<]+)',
        r'掌柜[：:]\s*([^\n<]+)',
    ]
    
    for pattern in shop_patterns:
        match = re.search(pattern, text)
        if match:
            product['shop_name'] = match.group(1).strip()
            break
    
    # 6. 提取商品ID
    id_match = re.search(r'id=(\d+)', html_content)
    if id_match:
        product['item_id'] = id_match.group(1)
    
    # 7. 提取商品参数
    # 找包含"材质"、"重量"、"尺寸"等关键词的文本
    param_keywords = ['材质', '重量', '尺寸', '规格', '品牌', '适用']
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) > 100:  # 跳过太长的行
            continue
        for keyword in param_keywords:
            if keyword in line and ('：' in line or ':' in line):
                parts = line.replace(':', '：').split('：', 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    product['params'][parts[0].strip()] = parts[1].strip()
    
    return product


def analyze_batch(products):
    """批量数据分析"""
    if not products:
        return
    
    print("\n" + "=" * 60)
    print("批量数据分析")
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
        try:
            sales = int(p.get('sales_count', '0'))
            if sales > 0:
                sales_list.append(sales)
        except:
            pass
    
    if sales_list:
        print(f"\n销量统计 ({len(sales_list)}个有销量):")
        print(f"  总销量: {sum(sales_list)} 件")
        print(f"  平均: {sum(sales_list)//len(sales_list)} 件")
        print(f"  最高: {max(sales_list)} 件")
    
    # 评价分析
    reviews_list = []
    for p in products:
        try:
            reviews = int(p.get('reviews_count', '0'))
            if reviews > 0:
                reviews_list.append(reviews)
        except:
            pass
    
    if reviews_list:
        print(f"\n评价统计 ({len(reviews_list)}个有评价):")
        print(f"  总评价: {sum(reviews_list)} 条")
        print(f"  平均: {sum(reviews_list)//len(reviews_list)} 条")


def main():
    print("=" * 60)
    print("淘宝商品详情页 MHTML 批量解析工具")
    print("=" * 60)
    print("自动读取当前目录下所有 .mhtml 和 .html 文件")
    print("=" * 60)
    
    # 查找文件
    mhtml_files = glob("*.mhtml") + glob("*.html")
    # 排除已生成的文件
    mhtml_files = [f for f in mhtml_files if not f.startswith('parsed_') and not f.startswith('竞品')]
    
    if not mhtml_files:
        print("\n⚠️ 未找到 .mhtml 或 .html 文件！")
        print("请确保文件在当前目录下")
        return
    
    print(f"\n找到 {len(mhtml_files)} 个文件:")
    for i, f in enumerate(mhtml_files, 1):
        print(f"  {i}. {f}")
    
    # 解析所有文件
    all_products = []
    success_count = 0
    
    for filepath in mhtml_files:
        try:
            print(f"\n处理: {filepath}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            html_content = extract_html_from_mhtml(content)
            product = extract_product_data(html_content, filepath)
            
            if product['title']:
                print(f"  ✓ 标题: {product['title'][:50]}...")
                print(f"  ✓ 价格: {product['price']}")
                print(f"  ✓ 销量: {product['sales_count']}")
                all_products.append(product)
                success_count += 1
            else:
                print(f"  ⚠️ 未能提取到标题")
        
        except Exception as e:
            print(f"  ❌ 错误: {e}")
    
    print(f"\n{'='*60}")
    print(f"解析完成: {success_count}/{len(mhtml_files)} 个文件成功")
    print(f"{'='*60}")
    
    if not all_products:
        print("\n未能提取到任何商品数据")
        return
    
    # 数据分析
    analyze_batch(all_products)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_file = f"parsed_products_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    print(f"\n✅ JSON已保存: {json_file}")
    
    # CSV
    csv_file = f"parsed_products_{timestamp}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            'filename', 'title', 'price', 'original_price', 
            'sales_count', 'reviews_count', 'shop_name', 'item_id', 'crawl_time'
        ])
        writer.writeheader()
        for p in all_products:
            writer.writerow({
                'filename': p['filename'],
                'title': p['title'],
                'price': p['price'],
                'original_price': p['original_price'],
                'sales_count': p['sales_count'],
                'reviews_count': p['reviews_count'],
                'shop_name': p['shop_name'],
                'item_id': p['item_id'],
                'crawl_time': p['crawl_time']
            })
    print(f"✅ CSV已保存: {csv_file}")
    
    # 汇总报告
    report_file = f"parsed_report_{timestamp}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("淘宝商品批量解析报告\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"解析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"文件总数: {len(mhtml_files)}\n")
        f.write(f"成功解析: {success_count}\n\n")
        
        f.write("商品列表:\n")
        f.write("-" * 60 + "\n")
        for i, p in enumerate(all_products, 1):
            f.write(f"{i}. {p['title']}\n")
            f.write(f"   价格: {p['price']}\n")
            f.write(f"   销量: {p['sales_count']}\n")
            f.write(f"   评价: {p['reviews_count']}\n\n")
    
    print(f"✅ 报告已保存: {report_file}")
    print("\n" + "=" * 60)
    print("全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
