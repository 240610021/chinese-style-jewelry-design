"""
将 MHTML 文件转换为 PDF + PNG 截图
"""
import os, re, quopri, json, time, random, base64, io
from playwright.sync_api import sync_playwright

MHTML_DIR = r"g:\Downloads\蔡规划\琢匠产品"
PDF_DIR = r"g:\Downloads\蔡规划\琢匠产品_PDF"
SCREENSHOT_DIR = r"g:\Downloads\蔡规划\琢匠产品_截图"
COOKIE_FILE = r"g:\Downloads\蔡规划\taobao_cookies.json"

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def extract_html_from_mhtml(filepath):
    """从MHTML文件中提取解码后的HTML"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 找到 text/html 部分
    idx = content.find('Content-Type: text/html')
    if idx < 0:
        return None, None
    
    html_part = content[idx:]
    blank = html_part.find('\n\n')
    if blank < 0:
        return None, None
    
    raw_qp = html_part[blank+2:]
    boundary_idx = raw_qp.find('------MultipartBoundary')
    if boundary_idx > 0:
        raw_qp = raw_qp[:boundary_idx]
    
    # Decode quoted-printable
    try:
        decoded_bytes = quopri.decodestring(raw_qp.encode('latin-1'))
        decoded = decoded_bytes.decode('utf-8', errors='ignore')
    except:
        decoded = raw_qp
    
    # Extract original URL
    url_match = re.search(r'Snapshot-Content-Location:\s*(https://[^\s]+)', content)
    original_url = url_match.group(1) if url_match else None
    
    return decoded, original_url

def get_product_id_from_filename(filename):
    """从文件名提取商品ID"""
    m = re.match(r'\d+_(\d+)_', filename)
    return m.group(1) if m else filename.replace('.mhtml', '')

mhtml_files = sorted([f for f in os.listdir(MHTML_DIR) if f.endswith('.mhtml')])

# 检查哪些已经转换过
done_ids = set()
for f in os.listdir(PDF_DIR):
    m = re.match(r'(\d+)_', f)
    if m:
        done_ids.add(m.group(1))
for f in os.listdir(SCREENSHOT_DIR):
    m = re.match(r'(\d+)_', f)
    if m:
        done_ids.add(m.group(1))

pending = []
for mf in mhtml_files:
    pid = get_product_id_from_filename(mf)
    if pid not in done_ids:
        pending.append(mf)

print(f"总MHTML: {len(mhtml_files)} 个")
print(f"已完成: {len(done_ids)} 个")
print(f"待转换: {len(pending)} 个")

if not pending:
    print("全部已完成！")
    exit(0)

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"]
    )
    
    context = browser.new_context(
        viewport={"width": 1280, "height": 900},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )
    
    # 加载 cookies
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
    
    page = context.new_page()
    
    success = 0
    fail = 0
    
    for i, filename in enumerate(pending, 1):
        filepath = os.path.join(MHTML_DIR, filename)
        pid = get_product_id_from_filename(filename)
        
        print(f"\n[{i}/{len(pending)}] {filename[:60]}...", end=" ")
        
        try:
            html_content, original_url = extract_html_from_mhtml(filepath)
            
            if not html_content:
                print("无法提取HTML")
                fail += 1
                continue
            
            # 用setContent加载HTML（允许加载外部CSS/JS）
            page.set_content(html_content, timeout=30000)
            
            # 等待渲染
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except:
                pass
            time.sleep(2)
            
            # 截图
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{pid}_截图.png")
            try:
                page.screenshot(path=screenshot_path, full_page=True, timeout=30000)
            except:
                page.screenshot(path=screenshot_path, timeout=30000)
            
            # 保存PDF
            pdf_path = os.path.join(PDF_DIR, f"{pid}_商品页.pdf")
            try:
                page.pdf(path=pdf_path, print_background=True, timeout=30000)
            except Exception as e:
                print(f"PDF保存失败: {e}")
            
            print(f"OK")
            success += 1
            
        except Exception as e:
            print(f"FAIL: {str(e)[:80]}")
            fail += 1
        
        # 随机延迟
        time.sleep(1 + random.random() * 2)
    
    print(f"\n===== 完成 =====")
    print(f"成功: {success}, 失败: {fail}")
    print(f"PDF保存至: {PDF_DIR}")
    print(f"截图保存至: {SCREENSHOT_DIR}")
    
    browser.close()