/**
 * 淘宝店铺商品抓取脚本（页面内版）
 * 使用方法：
 * 1. 用Chrome打开淘宝店铺首页：https://shop113403298.taobao.com/search.htm
 * 2. 确保已登录淘宝
 * 3. 按F12打开开发者工具 → 切换到Console（控制台）
 * 4. 复制本代码全部内容，粘贴到Console，按回车
 * 5. 脚本会自动滚动页面加载所有商品，然后下载CSV
 */

(async function() {
    'use strict';
    
    const SHOP_NAME = "琢匠";
    const MAX_SCROLL = 50;  // 最大滚动次数
    const SCROLL_DELAY = 2000;  // 每次滚动间隔（毫秒）
    
    let allProducts = [];
    let lastHeight = 0;
    let noChangeCount = 0;
    
    console.log('='.repeat(60));
    console.log('淘宝店铺商品抓取 - 琢匠（页面内版）');
    console.log('='.repeat(60));
    console.log('开始滚动页面加载商品...');
    
    // 滚动页面加载更多商品
    for (let i = 0; i < MAX_SCROLL; i++) {
        window.scrollTo(0, document.body.scrollHeight);
        await new Promise(r => setTimeout(r, SCROLL_DELAY));
        
        const currentHeight = document.body.scrollHeight;
        if (currentHeight === lastHeight) {
            noChangeCount++;
            if (noChangeCount >= 3) {
                console.log('页面高度不再变化，加载完成');
                break;
            }
        } else {
            noChangeCount = 0;
            lastHeight = currentHeight;
        }
        
        // 提取当前页面的商品
        const products = extractProducts();
        console.log(`第 ${i+1} 次滚动，当前提取到 ${products.length} 个商品`);
    }
    
    // 提取商品数据
    function extractProducts() {
        const products = [];
        
        // 淘宝店铺商品卡片选择器（多种尝试）
        const selectors = [
            '.item',                    // 通用
            '.J_MouserOnverReq',       // 淘宝经典
            '.grid-item',              // 网格布局
            '[data-spm="shop"]',       // 店铺模块
            '.product',                // 通用产品
            '.goods-item',             // 商品项
            '.Item',                   // 大写
            '[class*="item"]',         // 包含item
            '.shop-hesper-bd .item',   // 店铺主体
            '.shop-list .item',        // 店铺列表
        ];
        
        let items = [];
        for (const selector of selectors) {
            try {
                items = document.querySelectorAll(selector);
                if (items.length > 0) {
                    console.log(`  使用选择器: ${selector}, 找到 ${items.length} 个元素`);
                    break;
                }
            } catch (e) {}
        }
        
        // 如果没找到，尝试更宽泛的选择
        if (items.length === 0) {
            // 尝试找包含价格和标题的链接
            const links = document.querySelectorAll('a[href*="item"]');
            console.log(`  尝试从 ${links.length} 个商品链接提取...`);
            
            for (const link of links) {
                const card = link.closest('div');
                if (!card) continue;
                
                // 在卡片内查找价格和标题
                const titleEl = link.querySelector('.title, [class*="title"], span') || link;
                const priceEl = card.querySelector('.price, [class*="price"], .c-price, [class*="c-price"]');
                const salesEl = card.querySelector('.sale, [class*="sale"], [class*="sold"], [class*="deal"]');
                
                const title = titleEl.textContent?.trim() || '';
                const price = priceEl ? priceEl.textContent.trim() : '';
                const sales = salesEl ? salesEl.textContent.trim() : '';
                const url = link.href || '';
                
                // 提取item_id
                let itemId = '';
                const idMatch = url.match(/id=(\d+)/);
                if (idMatch) itemId = idMatch[1];
                
                if (title && price) {
                    products.push({
                        item_id: itemId,
                        title: title,
                        price: price,
                        sales: sales,
                        url: url,
                        crawl_time: new Date().toLocaleString()
                    });
                }
            }
        } else {
            // 从找到的元素提取
            for (const item of items) {
                try {
                    // 尝试多种方式获取标题
                    let title = '';
                    const titleSelectors = ['.title', '[class*="title"]', 'a', 'span', 'h3', 'h4'];
                    for (const sel of titleSelectors) {
                        const el = item.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            title = el.textContent.trim();
                            break;
                        }
                    }
                    
                    // 尝试获取价格
                    let price = '';
                    const priceSelectors = ['.price', '[class*="price"]', '.c-price', '[class*="c-price"]', '[class*="cost"]'];
                    for (const sel of priceSelectors) {
                        const el = item.querySelector(sel);
                        if (el && el.textContent.includes('¥')) {
                            price = el.textContent.trim();
                            break;
                        }
                    }
                    
                    // 尝试获取销量
                    let sales = '';
                    const salesSelectors = ['.sale', '[class*="sale"]', '[class*="sold"]', '[class*="deal"]', '[class*="pay"]'];
                    for (const sel of salesSelectors) {
                        const el = item.querySelector(sel);
                        if (el) {
                            sales = el.textContent.trim();
                            break;
                        }
                    }
                    
                    // 获取链接
                    let url = '';
                    const linkEl = item.querySelector('a[href*="item"]') || item.closest('a[href*="item"]');
                    if (linkEl) url = linkEl.href;
                    
                    // 提取item_id
                    let itemId = '';
                    const idMatch = url.match(/id=(\d+)/);
                    if (idMatch) itemId = idMatch[1];
                    
                    if (title && (price || url)) {
                        products.push({
                            item_id: itemId,
                            title: title,
                            price: price,
                            sales: sales,
                            url: url,
                            crawl_time: new Date().toLocaleString()
                        });
                    }
                } catch (e) {
                    console.log('  解析失败:', e.message);
                }
            }
        }
        
        // 去重
        const seen = new Set();
        const unique = [];
        for (const p of products) {
            if (p.item_id && !seen.has(p.item_id)) {
                seen.add(p.item_id);
                unique.push(p);
            } else if (!p.item_id && p.title && !seen.has(p.title)) {
                seen.add(p.title);
                unique.push(p);
            }
        }
        
        return unique;
    }
    
    // 执行提取
    allProducts = extractProducts();
    console.log(`\n共提取到 ${allProducts.length} 个唯一商品`);
    
    // 显示前5个
    console.log('\n前5个商品预览:');
    for (let i = 0; i < Math.min(5, allProducts.length); i++) {
        const p = allProducts[i];
        console.log(`  ${i+1}. ${p.title?.substring(0, 40) || '无标题'}...`);
        console.log(`     价格: ${p.price || '未获取'} | 销量: ${p.sales || '未获取'}`);
    }
    
    // 数据分析
    if (allProducts.length > 0) {
        console.log('\n' + '='.repeat(60));
        console.log('数据分析');
        console.log('='.repeat(60));
        
        // 价格分析
        const prices = [];
        for (const p of allProducts) {
            const priceStr = p.price?.replace(/[^\d.]/g, '') || '';
            const price = parseFloat(priceStr);
            if (price > 0) prices.push(price);
        }
        
        if (prices.length > 0) {
            const min = Math.min(...prices);
            const max = Math.max(...prices);
            const avg = prices.reduce((a, b) => a + b, 0) / prices.length;
            console.log(`价格统计 (${prices.length}个有价格):`);
            console.log(`  最低: ¥${min.toFixed(2)}`);
            console.log(`  最高: ¥${max.toFixed(2)}`);
            console.log(`  平均: ¥${avg.toFixed(2)}`);
            
            // 价格带
            const ranges = {
                '0-50元': 0, '50-100元': 0, '100-200元': 0,
                '200-500元': 0, '500-1000元': 0, '1000元以上': 0,
            };
            for (const p of prices) {
                if (p < 50) ranges['0-50元']++;
                else if (p < 100) ranges['50-100元']++;
                else if (p < 200) ranges['100-200元']++;
                else if (p < 500) ranges['200-500元']++;
                else if (p < 1000) ranges['500-1000元']++;
                else ranges['1000元以上']++;
            }
            console.log(`\n价格带分布:`);
            for (const [r, c] of Object.entries(ranges)) {
                if (c > 0) console.log(`  ${r}: ${c} 款 (${(c/prices.length*100).toFixed(1)}%)`);
            }
        }
        
        // 销量分析
        const salesList = [];
        for (const p of allProducts) {
            const match = p.sales?.match(/(\d+)/);
            if (match) salesList.push(parseInt(match[1]));
        }
        if (salesList.length > 0) {
            const total = salesList.reduce((a, b) => a + b, 0);
            console.log(`\n销量统计 (${salesList.length}个有销量):`);
            console.log(`  总销量: ${total} 件`);
            console.log(`  平均: ${Math.floor(total/salesList.length)} 件`);
            console.log(`  最高: ${Math.max(...salesList)} 件`);
        }
    }
    
    // 导出CSV
    function exportCSV() {
        if (allProducts.length === 0) return;
        
        const headers = Object.keys(allProducts[0]);
        const csvContent = [
            headers.join(','),
            ...allProducts.map(p => headers.map(h => {
                const val = p[h] || '';
                if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
                    return `"${val.replace(/"/g, '""')}"`;
                }
                return val;
            }).join(','))
        ].join('\n');
        
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${SHOP_NAME}_products_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`\n✅ CSV已下载: ${a.download}`);
    }
    
    // 导出JSON
    function exportJSON() {
        const jsonContent = JSON.stringify(allProducts, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${SHOP_NAME}_products_${new Date().toISOString().slice(0,10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`✅ JSON已下载: ${a.download}`);
    }
    
    exportCSV();
    exportJSON();
    
    console.log('\n全部完成！');
    
})();
