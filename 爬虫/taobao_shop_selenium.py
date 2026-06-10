#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺商品爬虫 - Selenium自动化版
功能：自动打开浏览器，模拟用户浏览，抓取全店商品
要求：已安装Chrome浏览器
安装依赖：pip install selenium webdriver-manager
"""

import time
import json
import csv
import os
import re
from datetime import datetime

# ============ 配置区域 ============

SHOP_NAME = "琢匠"
SHOP_SEARCH_URL = "https://shop113403298.taobao.com/search.htm"  # 店铺搜索页
OUTPUT_DIR = "output"
MAX_PAGES = 50  # 最大翻页数
PAGE_LOAD_WAIT = 3  # 页面加载等待时间（秒）

# ============ 核心代码 ============

def setup_driver():
    """配置并启动Chrome浏览器"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("请先安装依赖：")
        print("  pip install selenium webdriver-manager")
        return None, None
    
    print("正在启动Chrome浏览器...")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 无头模式（可选）
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 反检测
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # 执行CDP命令，进一步隐藏自动化特征
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })
    
    return driver, By


def extract_products_from_page(driver, By):
    """从当前页面提取商品数据"""
    products = []
    
    # 等待商品加载
    time.sleep(2)
    
    # 尝试多种选择器定位商品卡片
    selectors = [
        '.item',  # 通用
        '.J_MouserOnverReq',  # 淘宝经典
        '[data-category="auctions"] .item',
        '.grid-item',
        '.product',
        '.goods-item',
    ]
    
    items = []
    for selector in selectors:
        try:
            items = driver.find_elements(By.CSS_SELECTOR, selector)
            if len(items) > 0:
                print(f"  使用选择器: {selector}, 找到 {len(items)} 个元素")
                break
        except:
            continue
    
    if not items:
        print("  未找到商品元素，尝试通过链接定位...")
        # 通过商品链接定位
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="item.htm"]')
        print(f"  找到 {len(links)} 个商品链接")
        
        for link in links:
            try:
                # 向上查找父容器
                parent = link
                for _ in range(5):
                    parent = parent.find_element(By.XPATH, '..')
                    # 检查是否包含图片和价格
                    try:
                        img = parent.find_element(By.CSS_SELECTOR, 'img')
                        price_el = parent.find_element(By.XPATH, ".//*[contains(text(), '¥')]")
                        if img and price_el:
                            items.append(parent)
                            break
                    except:
                        continue
            except:
                continue
        
        print(f"  通过链接定位到 {len(items)} 个商品")
    
    # 解析每个商品
    for item in items:
        try:
            # 提取标题
            title = ""
            title_selectors = ['.title', '[class*="title"]', 'a[title]']
            for sel in title_selectors:
                try:
                    el = item.find_element(By.CSS_SELECTOR, sel)
                    title = el.get_attribute('title') or el.text
                    if title.strip():
                        break
                except:
                    continue
            
            # 提取价格
            price = ""
            try:
                price_el = item.find_element(By.XPATH, ".//*[contains(text(), '¥')]")
                price = price_el.text.strip()
            except:
                pass
            
            # 提取销量
            sales = ""
            sales_keywords = ['月销', '已售', '人付款', '销量']
            for keyword in sales_keywords:
                try:
                    sales_el = item.find_element(By.XPATH, f".//*[contains(text(), '{keyword}')]")
                    sales = sales_el.text.strip()
                    break
                except:
                    continue
            
            # 提取链接和ID
            url = ""
            item_id = ""
            try:
                link_el = item.find_element(By.CSS_SELECTOR, 'a[href*="item.htm"]')
                url = link_el.get_attribute('href')
                match = re.search(r'id=(\d+)', url)
                if match:
                    item_id = match.group(1)
            except:
                pass
            
            # 提取图片
            img_url = ""
            try:
                img = item.find_element(By.CSS_SELECTOR, 'img')
                img_url = img.get_attribute('src') or img.get_attribute('data-src')
            except:
                pass
            
            # 过滤无效数据
            if not title or len(title) < 3:
                continue
            
            # 排除非商品
            exclude = ['消费者保障', '保证金', '收藏店铺', '装修', '品质工厂', '所有分类']
            if any(k in title for k in exclude):
                continue
            
            products.append({
                "item_id": item_id,
                "title": title.strip(),
                "price": price,
                "sales": sales,
                "img_url": img_url,
                "url": url,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
        except Exception as e:
            continue
    
    return products


def click_next_page(driver, By):
    """点击下一页按钮"""
    try:
        # 尝试多种下一页按钮选择器
        next_selectors = [
            '.next',
            '.pagination-next',
            '[class*="next"]',
            'a[title="下一页"]',
            'button:contains("下一页")',
        ]
        
        for selector in next_selectors:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if next_btn.is_enabled() and next_btn.is_displayed():
                    # 检查是否是禁用状态
                    class_attr = next_btn.get_attribute('class') or ''
                    if 'disabled' in class_attr:
                        return False
                    
                    next_btn.click()
                    time.sleep(PAGE_LOAD_WAIT)
                    return True
            except:
                continue
        
        return False
    except:
        return False


def scroll_to_load(driver):
    """滚动页面加载更多商品"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def main():
    print("=" * 60)
    print("淘宝店铺商品爬虫 - Selenium自动化版")
    print("=" * 60)
    print(f"目标店铺: {SHOP_NAME}")
    print(f"店铺URL: {SHOP_SEARCH_URL}")
    print("=" * 60)
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 启动浏览器
    driver, By = setup_driver()
    if not driver:
        return
    
    try:
        # 打开店铺搜索页
        print(f"\n正在打开店铺搜索页...")
        driver.get(SHOP_SEARCH_URL)
        
        # 等待页面加载
        print(f"等待页面加载 ({PAGE_LOAD_WAIT}秒)...")
        time.sleep(PAGE_LOAD_WAIT)
        
        # 检查是否需要登录
        if "login" in driver.current_url or "登录" in driver.title:
            print("\n⚠️ 需要登录淘宝！")
            print("请在浏览器中手动登录，登录完成后按回车继续...")
            input()
        
        all_products = []
        seen_ids = set()
        
        # 逐页抓取
        for page in range(1, MAX_PAGES + 1):
            print(f"\n正在抓取第 {page} 页...")
            
            # 滚动加载
            scroll_to_load(driver)
            
            # 提取商品
            products = extract_products_from_page(driver, By)
            
            if not products:
                print("  本页未找到商品，可能已到达末尾")
                break
            
            # 去重
            new_products = []
            for p in products:
                if p['item_id'] and p['item_id'] not in seen_ids:
                    seen_ids.add(p['item_id'])
                    new_products.append(p)
                elif not p['item_id'] and p['title'] not in seen_ids:
                    seen_ids.add(p['title'])
                    new_products.append(p)
            
            all_products.extend(new_products)
            print(f"  本页 {len(products)} 个商品，新增 {len(new_products)} 个，累计 {len(all_products)} 个")
            
            # 显示前3个
            for i, p in enumerate(new_products[:3]):
                print(f"    {i+1}. {p['title'][:40]}... | {p['price']}")
            
            # 点击下一页
            if page < MAX_PAGES:
                has_next = click_next_page(driver, By)
                if not has_next:
                    print("  没有下一页了")
                    break
        
        print(f"\n抓取完成！共获取 {len(all_products)} 个商品")
        
        # 数据分析
        if all_products:
            print("\n" + "=" * 60)
            print("数据分析")
            print("=" * 60)
            
            # 价格分析
            prices = []
            for p in all_products:
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
            
            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # CSV
            csv_file = f"{OUTPUT_DIR}/{SHOP_NAME}_selenium_{timestamp}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=all_products[0].keys())
                writer.writeheader()
                writer.writerows(all_products)
            print(f"\nCSV已保存: {csv_file}")
            
            # JSON
            json_file = f"{OUTPUT_DIR}/{SHOP_NAME}_selenium_{timestamp}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            print(f"JSON已保存: {json_file}")
    
    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
