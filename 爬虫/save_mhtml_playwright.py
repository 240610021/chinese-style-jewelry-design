#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺商品MHTML保存 - Playwright版
特点：自动管理浏览器，不需要手动连接
"""

import time
import json
import os
import re
import random

# 配置
SHOP_URL = "https://coppertistwu.jiyoujia.com/search.htm"
OUTPUT_DIR = r"g:\Downloads\蔡规划\新建文件夹"
PROGRESS_FILE = r"g:\Downloads\蔡规划\爬虫\saved_mhtml_progress.json"


def save_mhtml_with_cdp(page, filepath):
    """使用CDP命令保存页面为MHTML"""
    client = page.context.new_cdp_session(page)
    response = client.send("Page.captureSnapshot", {"format": "mhtml"})
    mhtml = response.get("data", "")

    if mhtml:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            f.write(mhtml)
        return True
    return False


def main():
    from playwright.sync_api import sync_playwright

    print("=" * 60)
    print("淘宝店铺MHTML保存 - Playwright版")
    print("=" * 60)

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

    with sync_playwright() as p:
        # 启动浏览器（使用已安装的Chrome）
        print("\n正在启动浏览器...")

        # 尝试使用系统Chrome
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]

        executable_path = None
        for path in chrome_paths:
            if os.path.exists(path):
                executable_path = path
                break

        if executable_path:
            print(f"  使用Chrome: {executable_path}")
            browser = p.chromium.launch(
                executable_path=executable_path,
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
        else:
            print("  使用Playwright内置浏览器")
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )

        # 创建新页面
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()

        # 隐藏自动化特征
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        try:
            # 打开店铺页面
            print(f"\n正在打开店铺页面...")
            page.goto(SHOP_URL, wait_until='networkidle', timeout=30000)
            time.sleep(3)

            # 检查是否需要登录
            page_text = page.inner_text('body')
            if '请登录' in page_text and '亲，请登录' in page_text:
                print("\n⚠️ 需要登录淘宝！")
                print("请在浏览器中完成登录，然后按回车继续...")
                input()
                page.reload(wait_until='networkidle')
                time.sleep(3)

            # 提取所有商品
            print("\n正在提取商品...")
            all_products = []
            seen_ids = set()
            page_num = 1

            while True:
                print(f"\n--- 第 {page_num} 页 ---")

                # 滚动加载
                for _ in range(3):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)

                # 提取商品链接
                links = page.query_selector_all('a[href*="item.taobao.com/item.htm"]')
                print(f"  找到 {len(links)} 个链接")

                page_products = []
                for link in links:
                    try:
                        href = link.get_attribute('href') or ''
                        title = (link.get_attribute('title') or link.inner_text() or '').strip()

                        match = re.search(r'id=(\d+)', href)
                        if not match:
                            continue
                        item_id = match.group(1)

                        if item_id in seen_ids:
                            continue
                        seen_ids.add(item_id)

                        if not title or len(title) < 3:
                            continue

                        if any(k in title for k in ['消费者保障', '保证金', '收藏店铺', '装修', '定金']):
                            continue

                        if href.startswith('//'):
                            href = 'https:' + href

                        page_products.append({"item_id": item_id, "title": title, "url": href})
                    except:
                        continue

                print(f"  提取到 {len(page_products)} 个新商品")
                all_products.extend(page_products)

                for i, p in enumerate(page_products[:3]):
                    print(f"    {i+1}. {p['title'][:40]}...")

                # 点击下一页
                try:
                    next_btn = page.query_selector('a[title="下一页"]')
                    if next_btn and next_btn.is_visible():
                        next_btn.click()
                        time.sleep(5)
                        page_num += 1
                    else:
                        # URL翻页
                        current_url = page.url
                        match = re.search(r'[?&]page=(\d+)', current_url)
                        if match:
                            next_page = int(match.group(1)) + 1
                            next_url = re.sub(r'page=\d+', f'page={next_page}', current_url)
                            page.goto(next_url, wait_until='networkidle')
                            time.sleep(5)
                            page_num += 1
                        else:
                            print("  没有下一页了")
                            break
                except Exception as e:
                    print(f"  翻页结束: {e}")
                    break

                if page_num > 50:
                    break

            print(f"\n{'='*60}")
            print(f"共提取 {len(all_products)} 个商品")
            print(f"{'='*60}")

            # 过滤已保存
            to_save = [p for p in all_products if p['item_id'] not in saved_ids]
            print(f"待保存: {len(to_save)} 个")

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

                try:
                    page.goto(p['url'], wait_until='networkidle', timeout=30000)
                    time.sleep(3)

                    # 滚动页面
                    for _ in range(3):
                        page.evaluate("window.scrollBy(0, 500)")
                        time.sleep(1)

                    # 保存MHTML
                    title_clean = re.sub(r'[\\/:*?"<>|]', '_', p['title'])[:80]
                    filename = f"{title_clean}_{p['item_id']}-淘宝网.mhtml"
                    filepath = os.path.join(OUTPUT_DIR, filename)

                    if save_mhtml_with_cdp(page, filepath):
                        size = os.path.getsize(filepath)
                        print(f"  ✅ {filename} ({size//1024} KB)")
                        success += 1
                        saved_ids.add(p['item_id'])
                        with open(PROGRESS_FILE, 'w') as f:
                            json.dump({"saved_items": list(saved_ids)}, f)
                    else:
                        print(f"  ❌ MHTML内容为空")
                        fail += 1

                except Exception as e:
                    print(f"  ❌ 失败: {str(e)[:60]}")
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
            browser.close()
            print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
