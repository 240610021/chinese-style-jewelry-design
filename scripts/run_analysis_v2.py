#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import json
import csv
import quopri
from glob import glob
from bs4 import BeautifulSoup

TARGET_DIR = r"g:\Downloads\蔡规划\新建文件夹"

def decode_quoted_printable(text):
    try:
        return quopri.decodestring(text.encode()).decode('utf-8')
    except:
        return text

def extract_html_from_mhtml(content):
    # Find HTML part in MHTML
    html_start = content.find('<!DOCTYPE html>')
    if html_start == -1:
        html_start = content.find('<html')
    if html_start != -1:
        return content[html_start:]
    return content

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw = f.read()

    html_raw = extract_html_from_mhtml(raw)
    # Decode quoted-printable soft line breaks and encoded chars
    html = decode_quoted_printable(html_raw)

    soup = BeautifulSoup(html, 'html.parser')

    # Title
    title = ''
    title_tag = soup.find('title')
    if title_tag:
        t = title_tag.get_text(strip=True)
        if ' - ' in t:
            title = t.split(' - ')[0]
        else:
            title = t

    # Try to find price from page scripts or meta
    price = None
    # Look for price in script tags containing item data
    scripts = soup.find_all('script')
    for script in scripts:
        text = script.string if script.string else ''
        # Try to find price patterns in scripts
        m = re.search(r'"price"[:\s"]+(\d+\.?\d*)', text)
        if m:
            try:
                price = float(m.group(1))
                break
            except:
                pass
        m = re.search(r'"defaultItemPrice"[:\s"]+(\d+\.?\d*)', text)
        if m:
            try:
                price = float(m.group(1))
                break
            except:
                pass
        m = re.search(r'"itemPrice"[:\s"]+(\d+\.?\d*)', text)
        if m:
            try:
                price = float(m.group(1))
                break
            except:
                pass

    # If no price from script, try visible text
    if not price:
        text = soup.get_text(separator='\n')
        prices = []
        for line in text.splitlines():
            m = re.findall(r'¥\s*(\d+\.?\d*)', line)
            for p in m:
                try:
                    pv = float(p)
                    if 1 <= pv <= 999999:
                        prices.append(pv)
                except:
                    pass
        if prices:
            price = min(prices)

    # Sales
    sales = None
    text = soup.get_text(separator='\n')
    for line in text.splitlines():
        line = line.strip()
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

    # Shop name
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

def main():
    os.chdir(TARGET_DIR)
    files = glob('*.mhtml') + glob('*.html')
    files = [f for f in files if not f.startswith('parsed_') and not f.startswith('analyze') and not f.startswith('run_')]
    products = []
    for fp in files:
        try:
            data = parse_file(fp)
            products.append(data)
        except Exception as e:
            print(f'Error parsing {fp}: {e}')

    with open('parsed_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    with open('parsed_products.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['filename','title','price','sales','reviews','shop','item_id'])
        writer.writeheader()
        for p in products:
            writer.writerow(p)

    print(f'Parsed {len(products)} files.')
    print('Saved parsed_products.json and parsed_products.csv')

if __name__ == '__main__':
    main()
