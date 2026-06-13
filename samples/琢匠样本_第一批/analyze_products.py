#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import csv
from glob import glob
from bs4 import BeautifulSoup

def extract_html_from_mhtml(content):
    html_start = content.find('<!DOCTYPE html>')
    if html_start == -1:
        html_start = content.find('<html')
    if html_start != -1:
        return content[html_start:]
    return content

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    html = extract_html_from_mhtml(content)
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n')
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    title = ''
    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        if ' - ' in t:
            title = t.split(' - ')[0]
        else:
            title = t

    # price: look for strong prices in text
    prices = []
    for line in lines:
        m = re.findall(r'¥\s*(\d+\.?\d*)', line)
        for p in m:
            try:
                pv = float(p)
                if 1 <= pv <= 999999:
                    prices.append(pv)
            except:
                pass
    price = min(prices) if prices else None

    # sales
    sales = None
    for line in lines:
        m = re.search(r'(?:月销|已售|销量)[\s:：]*(\d+(?:\+?))', line)
        if m:
            try:
                sales = int(m.group(1).replace('+',''))
                break
            except:
                pass
        m = re.search(r'(\d+(?:\+?))\s*人付款', line)
        if m:
            try:
                sales = int(m.group(1).replace('+',''))
                break
            except:
                pass

    # reviews
    reviews = None
    for line in lines:
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

    # shop name
    shop = ''
    for line in lines:
        if '店铺' in line and ('：' in line or ':' in line):
            parts = re.split(r'[:：]', line, 1)
            if len(parts) == 2:
                shop = parts[1].strip()
                break

    # item id from url in content
    item_id = ''
    m = re.search(r'[?&]id=(\d+)', content)
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

def main():
    files = glob('*.mhtml') + glob('*.html')
    files = [f for f in files if not f.startswith('parsed_') and not f.startswith('analyze')]
    products = []
    for fp in files:
        try:
            data = parse_file(fp)
            products.append(data)
        except Exception as e:
            print(f'Error parsing {fp}: {e}')

    # Save JSON
    with open('parsed_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    # Save CSV
    with open('parsed_products.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','title','price','sales','reviews','shop','item_id'])
        writer.writeheader()
        for p in products:
            writer.writerow(p)

    print(f'Parsed {len(products)} files.')
    print('Saved parsed_products.json and parsed_products.csv')

if __name__ == '__main__':
    main()
