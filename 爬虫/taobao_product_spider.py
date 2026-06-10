#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺商品爬虫 - 琢匠全店抓取
功能：抓取指定淘宝店铺的所有商品信息
输出：CSV + JSON
"""

import requests
import json
import time
import random
import csv
import os
import re
from datetime import datetime
from urllib.parse import urljoin

# ============ 配置区域 ============

SHOP_NAME = "琢匠"
SHOP_URL = "https://shop113403298.taobao.com/"  # 琢匠淘宝主店

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": "thw=cn; aui=2027319991; arms_uid=8c80ab10-852c-48c5-9198-057eaa94bcc4; wwUserTip=false; _hvn_lgc_=0; t=c99716aea141b0efebf0cd8cfec73e61; _tb_token_=e67330496eb45; sca=738cd5aa; havana_sdkSilent=1780997540743; cna=W3twIm1ZODMCAQ6ZDBZxVAaU; 3PcFlag=1780968747872; sn=; csg=ab76eff2; lgc=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; cancelledSubSites=empty; dnk=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; existShop=MTc4MDk2ODc0OQ%3D%3D; tracknick=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; _cc_=U%2BGCWk%2F7og%3D%3D; _l_g_=Ug%3D%3D; sg=418; _nk_=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; sdkSilent=1780998340041; mtop_partitioned_detect=1; _m_h5_tk=5404b0c867e474a3a01bfc84eb82a849_1780996038673; _m_h5_tk_enc=41e0777b3e25ef355fa9c3ab0ee5fa2d; havana_lgc_exp=1812096076929; fastSlient=1780992076929; uc1=cookie14=UoYWPUm84tyVWQ%3D%3D&existShop=false&pas=0&cookie21=VT5L2FSpdeCjwGS%2FFqZpWg%3D%3D&cookie15=V32FPkk%2Fw0dUvg%3D%3D&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D; xlly_s=1; isg=BPX1oGF985MrhBThapBHxJFIEXGvcqmEIpeENXcZOWygThRAOsGXVYnemhL4FcE8; tfstk=hEdwk_9GBNOjfv19hcxWaVjqN1LO4hVbGsssKHSHylZ6oi120n-VftmO1I-ekUP6cdgAns-B4txfcFgV6sC0obYY4GLHJZDnnEmkWFCYJ0iSNbM4Y5pvI-jDm6fhPZfcmnVi8MbVy-qMms0e-MIhmsfDme0FkMjcisxm8ebYfSJLVpHe4e2fJwdFSmIkS-N0iB7aVgYZzSmZk54O0MdoAv8dYdx1JnlrYsKpnnb2xkmfBEveYN-6YYq8iw-7lAoHMn-9BUrnFBp6TTAe2PhHZjOeBhOgbqp9GHp2bKcumIodYUW5hzVqadA2AFdK1JusAe9JvtkbZCk93p-MTw7Ecs64hr7-GCwYH9fR8gg15-eAIwQFV2uUH-BhvwSS5N1..",
}

OUTPUT_DIR = "output"
DELAY_MIN = 3
DELAY_MAX = 6

# ============ 核心代码 ============

class TaobaoShopSpider:
    """淘宝店铺商品爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.products = []
        self.shop_id = None
        self.seller_id = None
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
    
    def _delay(self):
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
    
    def _get(self, url, params=None):
        """发送GET请求"""
        try:
            self._delay()
            resp = self.session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp
        except Exception as e:
            print(f"  ✗ 请求失败: {e}")
            return None
    
    def get_shop_info(self):
        """获取店铺基本信息，提取shopId和sellerId"""
        print(f"正在访问店铺首页: {SHOP_URL}")
        resp = self._get(SHOP_URL)
        if not resp:
            return False
        
        html = resp.text
        
        # 提取shopId
        shop_match = re.search(r'shopId["\']?\s*[:=]\s*["\']?(\d+)', html)
        if shop_match:
            self.shop_id = shop_match.group(1)
            print(f"  ✓ 获取到 shopId: {self.shop_id}")
        
        # 提取sellerId
        seller_match = re.search(r'sellerId["\']?\s*[:=]\s*["\']?(\d+)', html)
        if seller_match:
            self.seller_id = seller_match.group(1)
            print(f"  ✓ 获取到 sellerId: {self.seller_id}")
        
        # 备用方案：从URL提取
        if not self.shop_id:
            url_match = re.search(r'shop(\d+)', SHOP_URL)
            if url_match:
                self.shop_id = url_match.group(1)
                print(f"  ✓ 从URL提取 shopId: {self.shop_id}")
        
        return self.shop_id is not None
    
    def get_products_api(self, page=1, page_size=24):
        """
        通过淘宝搜索API获取店铺商品
        """
        if not self.shop_id:
            print("未获取到shopId，无法调用API")
            return []
        
        # 淘宝店铺内搜索API
        api_url = "https://s.taobao.com/search"
        
        params = {
            "q": "",
            "shop": self.shop_id,
            "s": (page - 1) * page_size,
            "n": page_size,
            "sort": "sale-desc",
            "filter": "reserve_price[0,]",
        }
        
        print(f"  正在请求第 {page} 页...")
        resp = self._get(api_url, params)
        if not resp:
            return []
        
        return self._parse_search_page(resp.text)
    
    def _parse_search_page(self, html):
        """解析搜索页面HTML，提取商品信息"""
        products = []
        
        # 淘宝搜索页商品卡片正则
        # 商品数据通常在g_page_config变量中
        config_match = re.search(r'g_page_config\s*=\s*({.+?});', html)
        if config_match:
            try:
                data = json.loads(config_match.group(1))
                items = data.get('mods', {}).get('itemlist', {}).get('data', {}).get('auctions', [])
                
                for item in items:
                    product = {
                        "item_id": item.get("nid", ""),
                        "title": item.get("title", "").replace("<span class=H>", "").replace("</span>", ""),
                        "price": item.get("view_price", ""),
                        "sales": item.get("view_sales", ""),
                        "location": item.get("item_loc", ""),
                        "url": f"https://detail.tmall.com/item.htm?id={item.get('nid', '')}" if item.get('shopcard', {}).get('isTmall') else f"https://item.taobao.com/item.htm?id={item.get('nid', '')}",
                        "is_tmall": item.get("shopcard", {}).get("isTmall", False),
                        "shop_name": item.get("nick", ""),
                        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    products.append(product)
                    print(f"    ✓ {product['title'][:30]}... 价格:{product['price']} 销量:{product['sales']}")
            except json.JSONDecodeError as e:
                print(f"  ✗ JSON解析失败: {e}")
        else:
            # 备用：正则直接匹配商品卡片
            print("  未找到g_page_config，尝试正则匹配...")
            item_pattern = re.compile(r'data-nid="(\d+)".*?<a[^>]*title="([^"]*)".*?(\d+\.\d+).*?([\d]+人付款)', re.S)
            matches = item_pattern.findall(html)
            for match in matches:
                product = {
                    "item_id": match[0],
                    "title": match[1],
                    "price": match[2],
                    "sales": match[3],
                    "url": f"https://item.taobao.com/item.htm?id={match[0]}",
                    "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                products.append(product)
        
        return products
    
    def crawl_all_products(self, max_pages=20):
        """抓取全店商品"""
        print("\n" + "=" * 60)
        print("开始抓取全店商品")
        print("=" * 60)
        
        if not self.get_shop_info():
            print("获取店铺信息失败，请检查Cookie是否有效")
            return
        
        all_products = []
        for page in range(1, max_pages + 1):
            products = self.get_products_api(page)
            if not products:
                print(f"  第 {page} 页无数据，可能已到达末尾")
                break
            all_products.extend(products)
            print(f"  第 {page} 页完成，本页 {len(products)} 条，累计 {len(all_products)} 条")
        
        self.products = all_products
        print(f"\n抓取完成！共获取 {len(all_products)} 条商品数据")
    
    def analyze_data(self):
        """简单数据分析"""
        if not self.products:
            return
        
        print("\n" + "=" * 60)
        print("数据分析")
        print("=" * 60)
        
        # 价格分析
        prices = []
        for p in self.products:
            try:
                price = float(p.get("price", "0").replace(",", ""))
                if price > 0:
                    prices.append(price)
            except:
                pass
        
        if prices:
            print(f"价格统计:")
            print(f"  最低: ¥{min(prices):.2f}")
            print(f"  最高: ¥{max(prices):.2f}")
            print(f"  平均: ¥{sum(prices)/len(prices):.2f}")
        
        # 销量分析
        sales_list = []
        for p in self.products:
            sales_str = p.get("sales", "")
            match = re.search(r'(\d+)', sales_str.replace(",", ""))
            if match:
                sales_list.append(int(match.group(1)))
        
        if sales_list:
            print(f"\n销量统计:")
            print(f"  总销量（估算）: {sum(sales_list)} 件")
            print(f"  平均销量: {sum(sales_list)//len(sales_list)} 件")
            print(f"  最高销量: {max(sales_list)} 件")
        
        # 价格带分布
        if prices:
            ranges = {
                "0-50元": 0,
                "50-100元": 0,
                "100-200元": 0,
                "200-500元": 0,
                "500-1000元": 0,
                "1000元以上": 0,
            }
            for p in prices:
                if p < 50: ranges["0-50元"] += 1
                elif p < 100: ranges["50-100元"] += 1
                elif p < 200: ranges["100-200元"] += 1
                elif p < 500: ranges["200-500元"] += 1
                elif p < 1000: ranges["500-1000元"] += 1
                else: ranges["1000元以上"] += 1
            
            print(f"\n价格带分布:")
            for r, c in ranges.items():
                if c > 0:
                    print(f"  {r}: {c} 款 ({c/len(prices)*100:.1f}%)")
    
    def save(self):
        """保存数据"""
        if not self.products:
            print("没有数据可保存")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CSV
        csv_file = f"{OUTPUT_DIR}/{SHOP_NAME}_products_{timestamp}.csv"
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.products[0].keys())
            writer.writeheader()
            writer.writerows(self.products)
        print(f"\nCSV已保存: {csv_file}")
        
        # JSON
        json_file = f"{OUTPUT_DIR}/{SHOP_NAME}_products_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
        print(f"JSON已保存: {json_file}")


def main():
    print("=" * 60)
    print("淘宝店铺商品爬虫 - 琢匠")
    print("=" * 60)
    print(f"目标店铺: {SHOP_NAME}")
    print(f"店铺URL: {SHOP_URL}")
    print("=" * 60)
    
    spider = TaobaoShopSpider()
    spider.crawl_all_products(max_pages=20)
    spider.analyze_data()
    spider.save()
    
    print("\n全部完成！")


if __name__ == "__main__":
    main()
