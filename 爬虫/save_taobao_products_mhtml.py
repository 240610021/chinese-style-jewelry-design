#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺商品MHTML自动保存工具
功能：模拟人类浏览行为，自动将店铺所有商品详情页保存为MHTML格式
原理：使用Selenium + Chrome DevTools Protocol的Page.captureSnapshot命令
效果：等同于浏览器"另存为 → 网页，单一文件"

使用方法：
1. 确保已安装Chrome浏览器
2. 安装依赖: pip install selenium webdriver-manager
3. 修改 config_mhtml.py 配置目标店铺
4. 运行: python save_taobao_products_mhtml.py
5. 在弹出的浏览器中手动登录淘宝
6. 登录完成后按回车，脚本自动开始保存

作者: AI Assistant
日期: 2026-06-10
"""

import time
import json
import os
import re
import random
from datetime import datetime
from selenium.webdriver.common.by import By

# 导入配置
try:
    from config_mhtml import (
        SHOP_NAME, SHOP_SEARCH_URL, OUTPUT_DIR, PROGRESS_FILE,
        BROWSER_EXE, BROWSER_USER_DATA, REMOTE_DEBUGGING_PORT,
        MIN_DELAY, MAX_DELAY, PAGE_LOAD_WAIT, SCROLL_TIMES, SCROLL_DELAY,
        MAX_PAGES, MAX_RETRIES, EXPLICIT_WAIT_TIMEOUT,
        FILENAME_TEMPLATE, ILLEGAL_CHARS, MAX_FILENAME_LENGTH
    )
except ImportError:
    print("错误: 找不到配置文件 config_mhtml.py")
    print("请确保 config_mhtml.py 与本脚本在同一目录")
    exit(1)


def setup_driver():
    """启动QQ浏览器并连接（全自动，复用已有登录状态）"""
    import subprocess
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("请先安装依赖：")
        print("  pip install selenium")
        return None

    # 第1步：启动QQ浏览器（带远程调试端口，复用用户数据）
    print(f"正在启动QQ浏览器...")
    print(f"  路径: {BROWSER_EXE}")

    if not os.path.exists(BROWSER_EXE):
        print(f"  ❌ QQ浏览器不存在: {BROWSER_EXE}")
        print("  请在 config_mhtml.py 中修改 BROWSER_EXE 路径")
        return None

    # 启动QQ浏览器（带调试端口）
    cmd = [
        BROWSER_EXE,
        f"--remote-debugging-port={REMOTE_DEBUGGING_PORT}",
        f"--user-data-dir={BROWSER_USER_DATA}",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  QQ浏览器已启动（调试端口: {REMOTE_DEBUGGING_PORT}）")
    except Exception as e:
        print(f"  ❌ 启动QQ浏览器失败: {e}")
        return None

    # 第2步：等待浏览器就绪
    print("  等待浏览器就绪...")
    time.sleep(5)

    # 第3步：连接到QQ浏览器
    print("  正在连接QQ浏览器...")
    max_connect_retries = 10
    for attempt in range(max_connect_retries):
        try:
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{REMOTE_DEBUGGING_PORT}")
            driver = webdriver.Chrome(options=chrome_options)
            print(f"  ✅ 成功连接到QQ浏览器")
            return driver
        except Exception as e:
            if attempt < max_connect_retries - 1:
                time.sleep(2)
            else:
                print(f"  ❌ 连接失败: {e}")
                print("  请检查QQ浏览器是否正常启动")
                return None

    return None


def check_login_status(driver):
    """检测页面是否被登录弹窗阻挡"""
    from selenium.webdriver.common.by import By

    # 检查URL是否跳转到登录页
    if "login" in driver.current_url.lower():
        return False

    # 检查页面是否有登录弹窗（多种选择器）
    login_indicators = [
        '#J_LoginBox',                    # 淘宝登录弹窗
        '.login-dialog',                  # 登录对话框
        '[class*="login"]',               # 任何含login的class
        '.qrcode-login',                  # 扫码登录
        '#fm-login-submit',               # 登录按钮
    ]

    for selector in login_indicators:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                if el.is_displayed():
                    return False
        except:
            continue

    # 检查页面是否包含"请登录"文字（在可见区域）
    try:
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        if '请登录' in body_text and '亲，请登录' in body_text:
            # 如果页面主要内容很少（被登录弹窗挡住），判定为未登录
            if len(body_text) < 500:
                return False
    except:
        pass

    return True


def wait_for_login(driver):
    """等待用户完成登录，循环检测直到登录成功"""
    print("\n" + "=" * 70)
    print("⚠️ 需要登录淘宝！")
    print("请在浏览器中手动完成登录操作")
    print("（支持密码登录、扫码登录、短信登录）")
    print("登录成功后脚本会自动继续...")
    print("=" * 70)

    max_wait = 300  # 最长等待5分钟
    check_interval = 3  # 每3秒检测一次
    waited = 0

    while waited < max_wait:
        time.sleep(check_interval)
        waited += check_interval

        # 刷新当前页面检测
        try:
            current_url = driver.current_url
            # 如果URL不再包含login，尝试访问店铺页检测
            if "login" not in current_url.lower():
                driver.get(SHOP_SEARCH_URL)
                time.sleep(3)
                if check_login_status(driver):
                    print(f"\n✅ 登录成功！（等待了 {waited} 秒）")
                    return True
        except:
            pass

        # 每30秒提示一次
        if waited % 30 == 0 and waited > 0:
            print(f"  等待登录中...（已等待 {waited} 秒，最长等待 {max_wait} 秒）")

    print("\n❌ 登录等待超时！请重新运行脚本")
    return False


def human_like_scroll(driver):
    """模拟人类滚动行为"""
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(SCROLL_TIMES):
        # 随机滚动距离（模拟人类不规律的滚动）
        scroll_distance = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

        # 随机停留时间（模拟人类阅读）
        wait_time = random.uniform(0.5, SCROLL_DELAY)
        time.sleep(wait_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # 尝试再滚动一次确认到底
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(1)
            final_height = driver.execute_script("return document.body.scrollHeight")
            if final_height == last_height:
                print(f"  滚动到底部（共{i+1}次）")
                break
        last_height = new_height

    # 滚动回顶部（模拟人类看完回到顶部）
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.5)


def extract_products_from_page(driver):
    """从当前页面提取商品链接和标题（适配极有家/淘宝店铺搜索页）"""
    from selenium.webdriver.common.by import By

    products = []

    # 等待商品加载
    time.sleep(2)

    # 极有家店铺搜索页结构：所有商品链接都是 a[href*="item.taobao.com/item.htm"]
    # 标题链接和图片链接交替排列，通过去重解决
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="item.taobao.com/item.htm"]')
    print(f"  找到 {len(links)} 个商品链接")

    # 调试：输出前3个链接的信息
    for i, link in enumerate(links[:3]):
        try:
            href = link.get_attribute('href') or ''
            title = (link.get_attribute('title') or link.text or '').strip()
            print(f"    链接{i+1}: href={href[:60]}, title={title[:30]}")
        except Exception as e:
            print(f"    链接{i+1}: 获取失败 - {e}")

    seen_ids = set()

    for link in links:
        try:
            href = link.get_attribute('href') or ''
            title = (link.get_attribute('title') or link.text or '').strip()

            # 提取商品ID
            match = re.search(r'id=(\d+)', href)
            if not match:
                continue
            item_id = match.group(1)

            # 去重
            if item_id in seen_ids:
                continue
            seen_ids.add(item_id)

            # 过滤无效数据
            if not title or len(title) < 3:
                continue

            # 排除非商品
            exclude = ['消费者保障', '保证金', '收藏店铺', '装修', '品质工厂', '所有分类', '定金']
            if any(k in title for k in exclude):
                continue

            # 补全协议
            if href.startswith('//'):
                href = 'https:' + href

            products.append({
                "item_id": item_id,
                "title": title,
                "url": href,
            })

        except Exception:
            continue

    print(f"  提取到 {len(products)} 个不重复商品")
    return products


def click_next_page(driver):
    """点击下一页按钮（适配极有家/淘宝店铺搜索页）"""
    from selenium.webdriver.common.by import By

    try:
        # 极有家搜索页的下一页按钮是文字链接"下一页"
        next_selectors = [
            'a[href*="下一页"]',
            'a[title="下一页"]',
            '.next',
            '.pagination-next',
            '[class*="next"]',
        ]

        for selector in next_selectors:
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                if next_btn.is_enabled() and next_btn.is_displayed():
                    class_attr = next_btn.get_attribute('class') or ''
                    if 'disabled' in class_attr:
                        return False

                    next_btn.click()
                    time.sleep(PAGE_LOAD_WAIT)
                    return True
            except:
                continue

        # 备用方案：通过URL参数翻页
        current_url = driver.current_url
        match = re.search(r'[?&]page=(\d+)', current_url)
        if match:
            current_page = int(match.group(1))
            next_url = re.sub(r'page=\d+', f'page={current_page + 1}', current_url)
            driver.get(next_url)
            time.sleep(PAGE_LOAD_WAIT)
            return True

        return False
    except:
        return False


def clean_filename(title, item_id):
    """清理文件名中的非法字符"""
    # 替换非法字符
    clean_title = re.sub(ILLEGAL_CHARS, '_', title)

    # 截断过长的标题
    max_title_len = MAX_FILENAME_LENGTH - len(FILENAME_TEMPLATE.replace('{title}', '').replace('{item_id}', item_id)) - 10
    if len(clean_title) > max_title_len:
        clean_title = clean_title[:max_title_len] + '...'

    # 生成文件名
    filename = FILENAME_TEMPLATE.format(title=clean_title, item_id=item_id)
    return filename


def save_page_as_mhtml(driver, url, title, item_id, output_dir):
    """使用CDP命令将页面保存为MHTML"""
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By

    retries = 0
    while retries < MAX_RETRIES:
        try:
            print(f"    正在打开商品页面...")
            driver.get(url)

            # 显式等待页面加载完成（等待商品标题元素出现）
            try:
                WebDriverWait(driver, EXPLICIT_WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'h1[data-spm="title"], .tb-detail-hd h1, h1'))
                )
            except:
                # 如果标题元素没找到，等待固定时间
                time.sleep(PAGE_LOAD_WAIT)

            # 模拟人类浏览：滚动查看商品详情
            print(f"    模拟人类浏览（滚动页面）...")
            human_like_scroll(driver)

            # 使用CDP命令获取MHTML内容
            print(f"    正在保存MHTML...")
            res = driver.execute_cdp_cmd('Page.captureSnapshot', {})
            mhtml_content = res.get('data', '')

            if not mhtml_content:
                print(f"    ⚠️ MHTML内容为空，重试中...")
                retries += 1
                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
                continue

            # 生成文件名
            filename = clean_filename(title, item_id)
            filepath = os.path.join(output_dir, filename)

            # 保存文件
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                f.write(mhtml_content)

            file_size = os.path.getsize(filepath)
            print(f"    ✅ 已保存: {filename} ({file_size/1024:.1f} KB)")

            return True

        except Exception as e:
            retries += 1
            print(f"    ❌ 保存失败（第{retries}次重试）: {str(e)[:100]}")
            if retries < MAX_RETRIES:
                time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    return False


def load_progress():
    """加载已保存的进度"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"saved_items": [], "last_run": None}


def save_progress(progress):
    """保存进度到文件"""
    progress["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def main():
    print("=" * 70)
    print("淘宝店铺商品MHTML自动保存工具")
    print("=" * 70)
    print(f"目标店铺: {SHOP_NAME}")
    print(f"店铺URL: {SHOP_SEARCH_URL}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 70)

    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"已创建输出目录: {OUTPUT_DIR}")

    # 加载进度
    progress = load_progress()
    saved_ids = set(progress.get("saved_items", []))
    print(f"已保存商品: {len(saved_ids)} 个")

    # 启动浏览器
    driver = setup_driver()
    if not driver:
        return

    try:
        # 打开店铺搜索页
        print(f"\n正在打开店铺搜索页...")
        driver.get(SHOP_SEARCH_URL)
        time.sleep(PAGE_LOAD_WAIT)

        # 检测登录状态（循环检测，自动等待用户登录）
        if not check_login_status(driver):
            if not wait_for_login(driver):
                return
            # 登录成功后重新加载店铺搜索页
            driver.get(SHOP_SEARCH_URL)
            time.sleep(PAGE_LOAD_WAIT)

        all_products = []
        seen_ids = set()

        # 逐页抓取商品列表
        for page in range(1, MAX_PAGES + 1):
            print(f"\n正在抓取第 {page} 页...")
            print(f"  当前URL: {driver.current_url}")

            # 模拟人类滚动
            human_like_scroll(driver)

            # 提取商品
            products = extract_products_from_page(driver)

            if not products:
                print("  本页未找到商品，可能已到达末尾")
                # 调试：输出页面源码前1000字符
                try:
                    page_text = driver.find_element(By.TAG_NAME, 'body').text[:500]
                    print(f"  页面文字预览: {page_text[:200]}...")
                except:
                    pass
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
                print(f"    {i+1}. {p['title'][:50]}...")

            # 点击下一页
            if page < MAX_PAGES:
                has_next = click_next_page(driver)
                if not has_next:
                    print("  没有下一页了")
                    break

        print(f"\n{'='*70}")
        print(f"商品列表抓取完成！共获取 {len(all_products)} 个商品")
        print(f"{'='*70}")

        # 过滤已保存的商品（断点续传）
        products_to_save = [p for p in all_products if p['item_id'] not in saved_ids]
        already_saved = len(all_products) - len(products_to_save)

        if already_saved > 0:
            print(f"跳过已保存: {already_saved} 个")
        print(f"待保存: {len(products_to_save)} 个")

        if not products_to_save:
            print("\n所有商品已保存完毕！")
            return

        # 逐个保存商品详情页为MHTML
        print(f"\n开始保存MHTML文件...")
        print("-" * 70)

        success_count = 0
        fail_count = 0
        start_time = time.time()

        for i, product in enumerate(products_to_save, 1):
            print(f"\n[{i}/{len(products_to_save)}] {product['title'][:50]}...")

            # 保存MHTML
            success = save_page_as_mhtml(
                driver,
                product['url'],
                product['title'],
                product['item_id'],
                OUTPUT_DIR
            )

            if success:
                success_count += 1
                saved_ids.add(product['item_id'])
                progress['saved_items'] = list(saved_ids)
                save_progress(progress)
            else:
                fail_count += 1

            # 随机延迟（模拟人类操作节奏）
            if i < len(products_to_save):
                delay = random.uniform(MIN_DELAY, MAX_DELAY)
                print(f"  等待 {delay:.1f} 秒...")
                time.sleep(delay)

        # 汇总报告
        elapsed = time.time() - start_time
        print(f"\n{'='*70}")
        print("保存完成！")
        print(f"{'='*70}")
        print(f"总计: {len(products_to_save)} 个商品")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"耗时: {elapsed/60:.1f} 分钟")
        print(f"平均: {elapsed/len(products_to_save):.1f} 秒/个")
        print(f"输出目录: {OUTPUT_DIR}")
        print(f"{'='*70}")

    finally:
        driver.quit()
        print("\n浏览器已关闭")


if __name__ == "__main__":
    main()
