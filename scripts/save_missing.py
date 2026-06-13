"""
补充保存遗漏的45个商品MHTML
更保守的策略：更长间隔、随机延迟、自动恢复
"""
import os, re, json, time, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

COOKIE_FILE = r"g:\Downloads\蔡规划\taobao_cookies.json"
MISSING_FILE = r"g:\Downloads\蔡规划\missing_products.json"
OUTPUT_DIR = r"g:\Downloads\蔡规划\琢匠产品"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(MISSING_FILE, 'r', encoding='utf-8') as f:
    products = json.load(f)

print(f"需要补存: {len(products)} 个商品")

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

def create_driver():
    d = webdriver.Chrome(options=options)
    d.maximize_window()
    # Load cookies
    d.get("https://www.taobao.com")
    time.sleep(2)
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    for c in cookies:
        try:
            if 'expiry' in c:
                c['expiry'] = int(c['expiry'])
            d.add_cookie(c)
        except:
            pass
    return d

driver = create_driver()
session_restarts = 0

success = 0
fail = 0

for i, prod in enumerate(products):
    item_id = prod['id']
    title = prod['title']
    url = prod['href']
    
    safe_title = title if title else item_id
    safe_title = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', safe_title)
    if len(safe_title) > 80:
        safe_title = safe_title[:80]
    filename = f"z_{item_id}_{safe_title}.mhtml"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(filepath):
        print(f"[{i+1}/{len(products)}] 已存在, 跳过 {item_id}")
        success += 1
        continue
    
    try:
        driver.get(url)
        # Wait 3-5 seconds randomly
        time.sleep(3 + random.random() * 2)
        
        result = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(result['data'])
        
        kb = len(result['data']) / 1024
        print(f"[{i+1}/{len(products)}] OK {item_id} ({kb:.0f} KB)")
        success += 1
        
    except Exception as e:
        err = str(e)
        if "invalid session id" in err.lower():
            print(f"[{i+1}/{len(products)}] 会话失效，重启浏览器...")
            try:
                driver.quit()
            except:
                pass
            session_restarts += 1
            if session_restarts > 3:
                print("重启次数过多，暂停30秒后重试...")
                time.sleep(30)
                session_restarts = 0
            driver = create_driver()
            # Retry this item
            i -= 1
            continue
        
        print(f"[{i+1}/{len(products)}] FAIL {item_id}: {err[:80]}")
        fail += 1
    
    # Random delay between items
    delay = 2 + random.random() * 3
    time.sleep(delay)

print(f"\n完成! 成功: {success}, 失败: {fail}, 总计: {len(products)}")
time.sleep(5)
driver.quit()