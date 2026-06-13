"""
琢匠COPPERTIST WU 店铺商品批量保存为MHTML
使用 Selenium + Chrome CDP
"""
import os
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

STORE_URL = "https://coppertistwu.jiyoujia.com/search.htm?search=y"
OUTPUT_DIR = r"g:\Downloads\蔡规划\琢匠产品"
SAVE_LIST_FILE = r"g:\Downloads\蔡规划\product_links.json"
COOKIE_FILE = r"g:\Downloads\蔡规划\taobao_cookies.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

print("正在启动 Chrome 浏览器...")
driver = webdriver.Chrome(options=options)
driver.maximize_window()

def check_logged_in():
    """检查是否已登录"""
    try:
        driver.get(STORE_URL + "&pageNum=1")
        time.sleep(4)
        products = driver.execute_script("""
            const results = [];
            document.querySelectorAll('a[href*="item.taobao.com/item.htm"]').forEach(a => {
                const match = a.href.match(/[?&]id=(\\d+)/);
                if (match) results.push(match[1]);
            });
            return results;
        """)
        return len(products) > 0
    except:
        return False

def wait_for_login(max_wait=300):
    """等待用户手动登录，最多等待 max_wait 秒"""
    start = time.time()
    while time.time() - start < max_wait:
        if "login" not in driver.current_url.lower() and "taobao.com" in driver.current_url:
            time.sleep(3)
            if check_logged_in():
                return True
        time.sleep(3)
    return False

try:
    # ========== 步骤0: 登录验证 ==========
    need_login = True
    
    # 尝试加载已保存的 cookies
    if os.path.exists(COOKIE_FILE):
        print("找到已保存的 cookies，尝试验证...")
        driver.get("https://www.taobao.com")
        time.sleep(2)
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        for cookie in cookies:
            try:
                if 'expiry' in cookie:
                    cookie['expiry'] = int(cookie['expiry'])
                driver.add_cookie(cookie)
            except:
                pass
        
        if check_logged_in():
            need_login = False
            print("Cookies 有效！")
        else:
            print("Cookies 已过期")
    
    if need_login:
        print("\n" + "=" * 60)
        print("请在弹出的 Chrome 窗口中登录淘宝（扫码或密码）")
        print("等待登录完成...（最多5分钟）")
        print("=" * 60)
        
        driver.get("https://login.taobao.com/")
        
        if wait_for_login(300):
            print("登录成功！")
            cookies = driver.get_cookies()
            with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cookies, f)
            print("Cookies 已保存，下次无需重新登录")
        else:
            print("登录超时，退出")
            driver.quit()
            exit(1)
    
    # ========== 步骤1: 收集所有商品链接 ==========
    print("\n" + "=" * 60)
    print("步骤1: 开始收集所有商品链接...")
    print("=" * 60)
    
    all_products = []
    seen_ids = set()
    
    for page_num in range(1, 10):
        url = f"{STORE_URL}&pageNum={page_num}"
        print(f"正在访问第 {page_num} 页...", end=" ")
        
        driver.get(url)
        time.sleep(3)
        
        products = driver.execute_script("""
            const results = [];
            const links = document.querySelectorAll('a[href*="item.taobao.com/item.htm"]');
            const seen = new Set();
            links.forEach(a => {
                const href = a.href;
                const match = href.match(/[?&]id=(\\d+)/);
                if (match && !seen.has(match[1])) {
                    seen.add(match[1]);
                    const img = a.querySelector('img');
                    let title = '';
                    if (img) {
                        title = img.getAttribute('alt') || img.getAttribute('title') || '';
                    }
                    if (!title) {
                        title = a.getAttribute('title') || a.textContent?.trim() || '';
                    }
                    results.push({
                        id: match[1],
                        href: 'https://item.taobao.com/item.htm?id=' + match[1],
                        title: title.substring(0, 200).replace(/[\\r\\n]/g, ' ').trim()
                    });
                }
            });
            return results;
        """)
        
        new_count = 0
        for prod in products:
            if prod['id'] not in seen_ids:
                seen_ids.add(prod['id'])
                all_products.append(prod)
                new_count += 1
        
        print(f"{len(products)} 个商品, 新增 {new_count}, 累计 {len(all_products)}")
        
        if new_count == 0:
            break
    
    with open(SAVE_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
    
    print(f"\n共收集到 {len(all_products)} 个商品链接")
    print(f"链接已保存到: {SAVE_LIST_FILE}")
    
    if not all_products:
        print("未找到任何商品！")
        driver.quit()
        exit(1)
    
    # ========== 步骤2: 逐个保存MHTML ==========
    print("\n" + "=" * 60)
    print(f"步骤2: 开始逐个保存商品页面为 MHTML（共 {len(all_products)} 个）...")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, prod in enumerate(all_products, 1):
        item_id = prod['id']
        title = prod['title']
        url = prod['href']
        
        safe_title = title if title else item_id
        safe_title = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', safe_title)
        if len(safe_title) > 80:
            safe_title = safe_title[:80]
        filename = f"{i:03d}_{item_id}_{safe_title}.mhtml"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"[{i}/{len(all_products)}] (跳过已存在)")
            success_count += 1
            continue
        
        try:
            driver.get(url)
            time.sleep(2)
            
            result = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result['data'])
            
            file_size = len(result['data']) / 1024
            print(f"[{i}/{len(all_products)}] {title[:40] or item_id} ({file_size:.0f} KB)")
            success_count += 1
            
        except Exception as e:
            print(f"[{i}/{len(all_products)}] {title[:40] or item_id} FAIL: {e}")
            fail_count += 1
        
        # 控制速度
        if i % 10 == 0:
            time.sleep(2)
        else:
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"完成! 成功: {success_count}, 失败: {fail_count}, 总计: {len(all_products)}")
    print(f"所有文件保存在: {OUTPUT_DIR}")
    print("=" * 60)
    
finally:
    print("\n10秒后关闭浏览器...")
    time.sleep(10)
    driver.quit()