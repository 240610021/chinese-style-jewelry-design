#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺商品MHTML保存 - 极简版
使用方法：
1. 先用QQ浏览器打开 https://coppertistwu.jiyoujia.com/search.htm 并登录
2. 保持QQ浏览器打开
3. 运行此脚本
"""

import time
import json
import os
import re
import random
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ============ 配置 ============
SHOP_NAME = "CoppertistWu"
SHOP_URL = "https://coppertistwu.jiyoujia.com/search.htm"
OUTPUT_DIR = r"g:\Downloads\蔡规划\新建文件夹"
PROGRESS_FILE = r"g:\Downloads\蔡规划\爬虫\saved_mhtml_progress.json"
BROWSER_EXE = r"C:\Program Files\Tencent\QQBrowser\QQBrowser.exe"
BROWSER_DATA = r"C:\Users\Administrator\AppData\Local\Tencent\QQBrowser\User Data"
DEBUG_PORT = 9222

# ============ 启动并连接浏览器 ============

def start_and_connect_browser():
    """启动Chrome浏览器（复用QQ浏览器的用户数据）"""
    print("=" * 60)
    print("淘宝店铺MHTML保存 - 极简版")
    print("=" * 60)

    # 方案1：尝试连接已打开的QQ浏览器（如果用户已手动启动）
    print("\n尝试连接已有浏览器...")
    for i in range(5):
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
            driver = webdriver.Chrome(options=options)
            print(f"  ✅ 成功连接到已有浏览器")
            print(f"  当前页面: {driver.current_url}")
            return driver
        except:
            time.sleep(1)

    # 方案2：启动新的Chrome，复用QQ浏览器的用户数据
    print("\n正在启动Chrome（复用QQ浏览器登录状态）...")

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    if not os.path.exists(chrome_path):
        print("❌ 找不到Chrome浏览器，请安装Chrome")
        return None

    # 启动Chrome（带调试端口，复用QQ浏览器的用户数据）
    cmd = [
        chrome_path,
        f"--remote-debugging-port={DEBUG_PORT}",
        f"--user-data-dir={BROWSER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  Chrome已启动（复用QQ浏览器数据）")
    except Exception as e:
        print(f"  启动失败: {e}")
        return None

    # 等待浏览器就绪
    print("  等待浏览器就绪...")
    time.sleep(6)

    # 连接浏览器
    print("  正在连接...")
    for i in range(15):
        try:
            options = Options()
            options.add_experimental_option("debuggerAddress", f"127.0.0.1:{DEBUG_PORT}")
            driver = webdriver.Chrome(options=options)
            print(f"  ✅ 连接成功")
            print(f"  当前页面: {driver.current_url}")
            return driver
        except Exception as e:
            if i == 0:
                print(f"    重试中...")
            time.sleep(2)

    print("  ❌ 连接失败")
    return None


# ============ 提取商品 ============

def extract_products(driver):
    """从当前页面提取所有商品"""
    print("\n正在提取商品...")

    # 打开店铺搜索页
    driver.get(SHOP_URL)
    time.sleep(5)

    # 检查是否需要登录
    page_text = driver.find_element(By.TAG_NAME, 'body').text
    if '请登录' in page_text and '亲，请登录' in page_text:
        print("\n⚠️ 需要登录淘宝！")
        print("请在QQ浏览器中完成登录，然后按回车继续...")
        input()
        driver.get(SHOP_URL)
        time.sleep(5)

    all_products = []
    seen_ids = set()
    page = 1

    while True:
        print(f"\n--- 第 {page} 页 ---")

        # 滚动加载
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # 提取商品链接
        links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="item.taobao.com/item.htm"]')
        print(f"  找到 {len(links)} 个链接")

        page_products = []
        for link in links:
            try:
                href = link.get_attribute('href') or ''
                title = (link.get_attribute('title') or link.text or '').strip()

                match = re.search(r'id=(\d+)', href)
                if not match:
                    continue
                item_id = match.group(1)

                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)

                if not title or len(title) < 3:
                    continue

                # 排除非商品
                if any(k in title for k in ['消费者保障', '保证金', '收藏店铺', '装修', '定金']):
                    continue

                if href.startswith('//'):
                    href = 'https:' + href

                page_products.append({"item_id": item_id, "title": title, "url": href})

            except:
                continue

        print(f"  提取到 {len(page_products)} 个新商品")
        all_products.extend(page_products)

        # 显示前3个
        for i, p in enumerate(page_products[:3]):
            print(f"    {i+1}. {p['title'][:40]}...")

        # 点击下一页
        try:
            # 尝试多种方式找下一页
            next_found = False
            for selector in ['a[title="下一页"]', '.next', 'a:contains("下一页")']:
                try:
                    btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if btn.is_displayed():
                        btn.click()
                        time.sleep(5)
                        next_found = True
                        break
                except:
                    continue

            if not next_found:
                # URL翻页
                current_url = driver.current_url
                match = re.search(r'[?&]page=(\d+)', current_url)
                if match:
                    next_page = int(match.group(1)) + 1
                    next_url = re.sub(r'page=\d+', f'page={next_page}', current_url)
                    driver.get(next_url)
                    time.sleep(5)
                else:
                    print("  没有下一页了")
                    break

            page += 1
            if page > 50:
                break

        except Exception as e:
            print(f"  翻页出错: {e}")
            break

    print(f"\n{'='*60}")
    print(f"共提取 {len(all_products)} 个商品")
    print(f"{'='*60}")
    return all_products


# ============ 保存MHTML ============

def save_mhtml(driver, product, output_dir):
    """保存单个商品为MHTML"""
    try:
        driver.get(product['url'])
        time.sleep(5)

        # 滚动页面
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)

        # 获取MHTML
        res = driver.execute_cdp_cmd('Page.captureSnapshot', {})
        mhtml = res.get('data', '')

        if not mhtml:
            return False

        # 清理文件名
        title = re.sub(r'[\\/:*?"<>|]', '_', product['title'])[:80]
        filename = f"{title}_{product['item_id']}-淘宝网.mhtml"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(mhtml)

        size = os.path.getsize(filepath)
        print(f"  ✅ {filename} ({size//1024} KB)")
        return True

    except Exception as e:
        print(f"  ❌ 失败: {str(e)[:60]}")
        return False


# ============ 主程序 ============

def main():
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 加载进度
    saved_ids = set()
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                data = json.load(f)
                saved_ids = set(data.get('saved_items', []))
        except:
            pass
    print(f"已保存: {len(saved_ids)} 个")

    # 启动浏览器
    driver = start_and_connect_browser()
    if not driver:
        return

    try:
        # 提取商品
        products = extract_products(driver)

        # 过滤已保存
        to_save = [p for p in products if p['item_id'] not in saved_ids]
        print(f"\n待保存: {len(to_save)} 个")

        if not to_save:
            print("所有商品已保存完毕！")
            return

        # 保存MHTML
        print(f"\n开始保存MHTML...")
        print("-" * 60)

        success = 0
        fail = 0

        for i, p in enumerate(to_save, 1):
            print(f"\n[{i}/{len(to_save)}] {p['title'][:40]}...")

            if save_mhtml(driver, p, OUTPUT_DIR):
                success += 1
                saved_ids.add(p['item_id'])
                # 保存进度
                with open(PROGRESS_FILE, 'w') as f:
                    json.dump({"saved_items": list(saved_ids)}, f)
            else:
                fail += 1

            # 随机延迟
            if i < len(to_save):
                delay = random.uniform(3, 6)
                print(f"  等待 {delay:.1f} 秒...")
                time.sleep(delay)

        # 汇总
        print(f"\n{'='*60}")
        print("保存完成！")
        print(f"成功: {success}  失败: {fail}")
        print(f"输出: {OUTPUT_DIR}")
        print(f"{'='*60}")

    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
