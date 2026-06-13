"""
琢匠COPPERTIST WU 店铺商品批量保存为MHTML
步骤1: 收集所有商品链接
步骤2: 逐个访问并保存为MHTML
"""
import asyncio
import os
import re
import json
from playwright.async_api import async_playwright

STORE_URL = "https://coppertistwu.jiyoujia.com/search.htm?search=y"
OUTPUT_DIR = r"g:\Downloads\蔡规划\琢匠产品"
SAVE_LIST_FILE = r"g:\Downloads\蔡规划\product_links.json"

# 从已登录的MCP浏览器导出的cookies
COOKIE_STRING = "cna=VrWvItWRE20CAXFaVGjDFR0O; xlly_s=1; lid=%E5%8C%97%E6%96%97%E7%81%AC%E6%98%9F%E8%BE%B02014; dnk=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; uc1=pas=0&cookie16=VFC%2FuZ9az08KUQ56dCrZDlbNdA%3D%3D&cookie21=U%2BGCWk%2F7ow08GIhZA1V8cQ%3D%3D&existShop=false&cookie15=U%2BGCWk%2F75gdr5Q%3D%3D&cookie14=UoYWPA2CoshKJA%3D%3D; tracknick=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; _l_g_=Ug%3D%3D; havana_lgc_exp=1812417712234; unb=2027319991; lgc=; login=true; _nk_=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; cancelledSubSites=empty; sg=418; t=1bebca4fba07e331de0abbeb172a5828; csg=8073d114; sn=; _tb_token_=eee669b7351df; _m_h5_c=0f1e191d8b3c008cb94f70174cc9cd83_1781323200736%3B4c14f01044e1b51e82f447d1da9aa580; isg=BBwcq4gmmgNDGW7bYVV50YnC7TrOlcC_5baL9_YdKIfqQbzLHqWQT5Ljo6m5UvgX; tfstk=gL2sHLG1IFY1UNjOkFSeV3n2OpMfzMWzkniYqopwDAHtlrZ0D5oqu5uxDuESMoPw_r9Y5PsiMNDahyZYPGmVS-PBcu4Qljjiuq3buoFNYTWzjlDmHK_PUTkz2bsaCqLqHADp8gXWHTWzjlHmHa7PUSSIem09MKUx6XBKq2dtDcUxpXnrJdnvBx3dAm0KHxHYkkIIm2ntHxUYvMimJjyBVm1sSls0YFzMqbu8X29vh3ms64BoRKpYdcTryl1kHKeIff2UMF5OOfPYqb2act9nQuNKp0rGCpM8X0aZ8zBJdvEUvrlutZvrQywjNJlMDCEQhVG8BXt2nuMIDrhbta9rfAPINRNGmeETzVN-Io-57kG7ObmK9nOtQ7rznbeOCU0EZmaZ8zBJdvhA4mvrPMm9GHGkhDgPAMODiMjYuSyqZWcZ6DmsTMsBWSctxDgPAMODifnnf0SCAFFc."

def parse_cookies(cookie_string):
    """解析cookie字符串为Playwright格式"""
    cookies = []
    for item in cookie_string.split("; "):
        if "=" in item:
            name, value = item.split("=", 1)
            cookies.append({
                "name": name,
                "value": value,
                "domain": ".taobao.com",
                "path": "/"
            })
            cookies.append({
                "name": name,
                "value": value,
                "domain": ".jiyoujia.com",
                "path": "/"
            })
    return cookies

async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        )
        
        # 设置cookies
        cookie_list = parse_cookies(COOKIE_STRING)
        await context.add_cookies(cookie_list)
        
        page = await context.new_page()
        
        # ========== 步骤1: 收集所有商品链接 ==========
        print("=" * 60)
        print("步骤1: 开始收集所有商品链接...")
        print("=" * 60)
        
        all_products = []
        seen_ids = set()
        
        for page_num in range(1, 10):
            url = f"{STORE_URL}&pageNum={page_num}"
            print(f"\n正在访问第 {page_num} 页: {url}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)  # 等待动态内容加载
                
                # 提取商品链接
                products = await page.evaluate("""() => {
                    const results = [];
                    const links = document.querySelectorAll('a[href*="item.taobao.com/item.htm"]');
                    const seen = new Set();
                    links.forEach(a => {
                        const href = a.href;
                        const match = href.match(/[?&]id=(\\\\d+)/);
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
                                title: title.substring(0, 200).replace(/[\\\\r\\\\n]/g, ' ').trim()
                            });
                        }
                    });
                    return results;
                }""")
                
                new_count = 0
                for prod in products:
                    if prod['id'] not in seen_ids:
                        seen_ids.add(prod['id'])
                        all_products.append(prod)
                        new_count += 1
                
                print(f"  第 {page_num} 页: 找到 {len(products)} 个商品, 新增 {new_count} 个, 累计 {len(all_products)} 个")
                
                # 如果新增为0，说明可能已经到底了
                if new_count == 0:
                    break
                    
            except Exception as e:
                print(f"  第 {page_num} 页出错: {e}")
                # 检查是否需要登录
                if "login" in page.url.lower():
                    print("\n!!! 需要登录！cookies可能已过期，需要重新获取")
                    break
        
        # 保存链接列表
        with open(SAVE_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        print(f"\n共收集到 {len(all_products)} 个商品链接")
        print(f"链接已保存到: {SAVE_LIST_FILE}")
        
        if not all_products:
            print("未找到任何商品，请检查登录状态后重试")
            await browser.close()
            return
        
        # ========== 步骤2: 逐个保存MHTML ==========
        print("\n" + "=" * 60)
        print("步骤2: 开始逐个保存商品页面为 MHTML...")
        print(f"预计需要保存 {len(all_products)} 个商品")
        print("=" * 60)
        
        success_count = 0
        fail_count = 0
        
        for i, prod in enumerate(all_products, 1):
            item_id = prod['id']
            title = prod['title']
            url = prod['href']
            
            # 生成安全的文件名
            safe_title = title if title else item_id
            safe_title = re.sub(r'[\\/:*?"<>|\r\n\t]', '_', safe_title)
            if len(safe_title) > 80:
                safe_title = safe_title[:80]
            filename = f"{i:03d}_{item_id}_{safe_title}.mhtml"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # 如果文件已存在，跳过
            if os.path.exists(filepath):
                print(f"[{i}/{len(all_products)}] 已存在，跳过")
                success_count += 1
                continue
            
            print(f"[{i}/{len(all_products)}] 正在保存: {title[:60] or item_id}...")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(2000)
                
                # 使用 CDP 保存为 MHTML
                cdp = await page.context.new_cdp_session(page)
                result = await cdp.send("Page.captureSnapshot", {"format": "mhtml"})
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(result['data'])
                
                success_count += 1
                file_size = len(result['data']) / 1024
                print(f"  OK ({file_size:.0f} KB)")
                
            except Exception as e:
                fail_count += 1
                print(f"  FAIL: {e}")
            
            # 控制速度，避免被反爬
            if i % 5 == 0:
                await page.wait_for_timeout(2000)
            else:
                await page.wait_for_timeout(500)
        
        print("\n" + "=" * 60)
        print(f"完成! 成功: {success_count}, 失败: {fail_count}, 总计: {len(all_products)}")
        print(f"所有文件保存在: {OUTPUT_DIR}")
        print("=" * 60)
        
        # 等待用户查看结果
        print("\n浏览器将在10秒后关闭...")
        await asyncio.sleep(10)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())