/**
 * 淘宝店铺商品抓取脚本
 * 使用方法：
 * 1. 用Chrome打开淘宝店铺首页：https://shop113403298.taobao.com/
 * 2. 确保已登录淘宝
 * 3. 按F12打开开发者工具 → 切换到Console（控制台）
 * 4. 复制本代码全部内容，粘贴到Console，按回车
 * 5. 等待抓取完成，会自动下载CSV文件
 */

(async function() {
    'use strict';
    
    const SHOP_NAME = "琢匠";
    const MAX_PAGES = 20;  // 最大抓取页数
    const DELAY_MIN = 3000;  // 最小延迟（毫秒）
    const DELAY_MAX = 6000;  // 最大延迟（毫秒）
    
    let allProducts = [];
    
    // 延迟函数
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    function randomDelay() {
        const ms = Math.floor(Math.random() * (DELAY_MAX - DELAY_MIN) + DELAY_MIN);
        return delay(ms);
    }
    
    // 解析商品数据
    function parseProducts(html) {
        const products = [];
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // 尝试多种选择器匹配商品卡片
        const selectors = [
            '.item',           // 常见商品卡片
            '.J_MouserOnverReq',
            '.grid-item',
            '[data-category="auctions"] .item',
            '.product',
            '.goods-item',
        ];
        
        let items = [];
        for (const selector of selectors) {
            items = doc.querySelectorAll(selector);
            if (items.length > 0) {
                console.log(`  使用选择器: ${selector}, 找到 ${items.length} 个商品`);
                break;
            }
        }
        
        if (items.length === 0) {
            // 尝试从g_page_config解析
            const configMatch = html.match(/g_page_config\s*=\s*({.+?});/);
            if (configMatch) {
                try {
                    const data = JSON.parse(configMatch[1]);
                    const auctions = data?.mods?.itemlist?.data?.auctions || [];
                    console.log(`  从g_page_config解析到 ${auctions.length} 个商品`);
                    
                    for (const item of auctions) {
                        products.push({
                            item_id: item.nid || '',
                            title: (item.title || '').replace(/<[^>]+>/g, ''),
                            price: item.view_price || '',
                            sales: item.view_sales || '',
                            location: item.item_loc || '',
                            url: item.detail_url || `https://item.taobao.com/item.htm?id=${item.nid}`,
                            is_tmall: item.shopcard?.isTmall || false,
                            shop_name: item.nick || '',
                            crawl_time: new Date().toLocaleString()
                        });
                    }
                } catch (e) {
                    console.log('  g_page_config解析失败:', e.message);
                }
            }
        } else {
            // 从DOM解析
            for (const item of items) {
                try {
                    const titleEl = item.querySelector('.title, .product-title, a[title]');
                    const priceEl = item.querySelector('.price, .c-price, .text-price');
                    const salesEl = item.querySelector('.sale-num, .deal-cnt, [class*="sale"]');
                    const linkEl = item.querySelector('a[href]');
                    
                    const title = titleEl ? (titleEl.getAttribute('title') || titleEl.textContent).trim() : '';
                    const price = priceEl ? priceEl.textContent.trim() : '';
                    const sales = salesEl ? salesEl.textContent.trim() : '';
                    const url = linkEl ? linkEl.href : '';
                    
                    // 提取item_id
                    let itemId = '';
                    const idMatch = url.match(/id=(\d+)/);
                    if (idMatch) itemId = idMatch[1];
                    
                    if (title) {
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
                    console.log('  解析商品失败:', e.message);
                }
            }
        }
        
        return products;
    }
    
    // 抓取单页
    async function fetchPage(page) {
        const pageSize = 24;
        const s = (page - 1) * pageSize;
        
        // 构建搜索URL（店铺内搜索）
        const url = `https://s.taobao.com/search?q=&shop=113403298&s=${s}&n=${pageSize}&sort=sale-desc`;
        
        console.log(`正在请求第 ${page} 页...`);
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                },
                credentials: 'include'  // 携带Cookie
            });
            
            if (!response.ok) {
                console.log(`  ✗ 请求失败: ${response.status}`);
                return [];
            }
            
            const html = await response.text();
            const products = parseProducts(html);
            
            for (const p of products) {
                console.log(`    ✓ ${p.title?.substring(0, 30) || '无标题'}... 价格:${p.price} 销量:${p.sales}`);
            }
            
            return products;
        } catch (e) {
            console.log(`  ✗ 请求异常: ${e.message}`);
            return [];
        }
    }
    
    // 主抓取流程
    async function crawl() {
        console.log('='.repeat(60));
        console.log('淘宝店铺商品抓取 - 琢匠');
        console.log('='.repeat(60));
        console.log(`目标店铺: ${SHOP_NAME}`);
        console.log(`最大页数: ${MAX_PAGES}`);
        console.log('='.repeat(60));
        
        for (let page = 1; page <= MAX_PAGES; page++) {
            await randomDelay();
            const products = await fetchPage(page);
            
            if (products.length === 0) {
                console.log(`第 ${page} 页无数据，可能已到达末尾`);
                break;
            }
            
            allProducts.push(...products);
            console.log(`第 ${page} 页完成，本页 ${products.length} 条，累计 ${allProducts.length} 条`);
        }
        
        console.log('\n' + '='.repeat(60));
        console.log(`抓取完成！共获取 ${allProducts.length} 条商品数据`);
        console.log('='.repeat(60));
    }
    
    // 数据分析
    function analyze() {
        if (allProducts.length === 0) return;
        
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
            console.log(`价格统计:`);
            console.log(`  最低: ¥${min.toFixed(2)}`);
            console.log(`  最高: ¥${max.toFixed(2)}`);
            console.log(`  平均: ¥${avg.toFixed(2)}`);
        }
        
        // 销量分析
        const salesList = [];
        for (const p of allProducts) {
            const match = p.sales?.match(/(\d+)/);
            if (match) salesList.push(parseInt(match[1]));
        }
        
        if (salesList.length > 0) {
            const total = salesList.reduce((a, b) => a + b, 0);
            const avg = Math.floor(total / salesList.length);
            const max = Math.max(...salesList);
            console.log(`\n销量统计:`);
            console.log(`  总销量（估算）: ${total} 件`);
            console.log(`  平均销量: ${avg} 件`);
            console.log(`  最高销量: ${max} 件`);
        }
        
        // 价格带分布
        if (prices.length > 0) {
            const ranges = {
                '0-50元': 0,
                '50-100元': 0,
                '100-200元': 0,
                '200-500元': 0,
                '500-1000元': 0,
                '1000元以上': 0,
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
                if (c > 0) {
                    console.log(`  ${r}: ${c} 款 (${(c/prices.length*100).toFixed(1)}%)`);
                }
            }
        }
    }
    
    // 导出CSV
    function exportCSV() {
        if (allProducts.length === 0) {
            console.log('没有数据可导出');
            return;
        }
        
        const headers = Object.keys(allProducts[0]);
        const csvContent = [
            headers.join(','),
            ...allProducts.map(p => headers.map(h => {
                const val = p[h] || '';
                // 处理包含逗号或引号的值
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
        
        console.log(`\nCSV已下载: ${a.download}`);
    }
    
    // 导出JSON
    function exportJSON() {
        if (allProducts.length === 0) return;
        
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
        
        console.log(`JSON已下载: ${a.download}`);
    }
    
    // 执行
    await crawl();
    analyze();
    exportCSV();
    exportJSON();
    
    console.log('\n全部完成！');
    
})();
