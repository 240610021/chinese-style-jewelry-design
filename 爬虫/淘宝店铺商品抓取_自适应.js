/**
 * 淘宝店铺商品抓取脚本（自适应版）
 * 使用方法：
 * 1. 用Chrome打开淘宝店铺搜索页：https://shop113403298.taobao.com/search.htm
 * 2. 确保已登录淘宝，页面已加载商品
 * 3. 按F12 → Console
 * 4. 复制本代码全部内容，粘贴到Console，按回车
 * 5. 脚本会自动尝试多种方式提取商品，并提示结果
 */

(async function() {
    'use strict';
    
    console.log('='.repeat(60));
    console.log('淘宝店铺商品抓取 - 琢匠（自适应版）');
    console.log('='.repeat(60));
    
    // ====== 第一步：分析页面结构 ======
    console.log('\n【第一步】分析页面结构...');
    
    // 获取页面所有div元素，分析可能的商品容器
    const allDivs = document.querySelectorAll('div');
    console.log(`页面共有 ${allDivs.length} 个div元素`);
    
    // 寻找包含商品特征的元素
    function findProductContainers() {
        const candidates = [];
        
        // 策略1：找包含价格符号¥的元素
        for (const el of allDivs) {
            if (el.textContent.includes('¥') && el.children.length >= 2) {
                const rect = el.getBoundingClientRect();
                if (rect.width > 100 && rect.height > 100) {
                    candidates.push({
                        element: el,
                        reason: '包含¥符号且有子元素',
                        class: el.className
                    });
                }
            }
        }
        
        // 策略2：找包含"月销"、"已售"、"人付款"的元素
        if (candidates.length === 0) {
            for (const el of allDivs) {
                const text = el.textContent;
                if ((text.includes('月销') || text.includes('已售') || text.includes('人付款') || text.includes('销量')) 
                    && el.children.length >= 2) {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 100) {
                        candidates.push({
                            element: el,
                            reason: '包含销量关键词',
                            class: el.className
                        });
                    }
                }
            }
        }
        
        // 策略3：找包含商品链接的元素
        if (candidates.length === 0) {
            const links = document.querySelectorAll('a[href*="item"]');
            for (const link of links) {
                const parent = link.closest('div');
                if (parent && parent.children.length >= 2) {
                    const rect = parent.getBoundingClientRect();
                    if (rect.width > 100 && rect.height > 100) {
                        candidates.push({
                            element: parent,
                            reason: '包含商品链接',
                            class: parent.className
                        });
                    }
                }
            }
        }
        
        return candidates;
    }
    
    const containers = findProductContainers();
    console.log(`找到 ${containers.length} 个可能的商品容器`);
    
    if (containers.length === 0) {
        console.log('\n⚠️ 未找到商品容器，可能页面未加载完成或结构特殊');
        console.log('请确保：');
        console.log('1. 页面已完全加载（看到商品列表）');
        console.log('2. 当前URL是店铺搜索页，如：https://shop113403298.taobao.com/search.htm');
        return;
    }
    
    // 显示前5个候选容器
    console.log('\n候选容器（前5个）：');
    for (let i = 0; i < Math.min(5, containers.length); i++) {
        const c = containers[i];
        console.log(`  ${i+1}. class="${c.class?.substring(0, 50) || '无'}" | ${c.reason}`);
    }
    
    // ====== 第二步：提取商品数据 ======
    console.log('\n【第二步】提取商品数据...');
    
    const allProducts = [];
    const seen = new Set();
    
    // 使用第一个候选容器作为参考，找同类元素
    const sampleContainer = containers[0].element;
    const parent = sampleContainer.parentElement;
    
    // 尝试获取同类商品
    let items = [];
    
    // 方法1：通过相同class找
    if (sampleContainer.className) {
        const classSelector = sampleContainer.className.split(' ').filter(c => c).map(c => `.${c}`).join('');
        try {
            items = document.querySelectorAll(classSelector);
            console.log(`方法1（相同class）: 找到 ${items.length} 个`);
        } catch (e) {}
    }
    
    // 方法2：通过父元素的直接子元素
    if (items.length === 0 && parent) {
        items = parent.children;
        console.log(`方法2（父元素子元素）: 找到 ${items.length} 个`);
    }
    
    // 方法3：遍历所有候选容器
    if (items.length === 0) {
        items = containers.map(c => c.element);
        console.log(`方法3（候选容器）: 找到 ${items.length} 个`);
    }
    
    console.log(`\n开始解析 ${items.length} 个商品...`);
    
    for (let i = 0; i < items.length; i++) {
        const item = items[i];
        try {
            // 提取标题 - 多种策略
            let title = '';
            const titleSelectors = [
                'a[title]', '.title', '[class*="title"]', 
                'h3', 'h4', 'span', 'a'
            ];
            for (const sel of titleSelectors) {
                const el = item.querySelector(sel);
                if (el) {
                    title = el.getAttribute('title') || el.textContent;
                    title = title.trim();
                    if (title && title.length > 5) break;
                }
            }
            
            // 提取价格
            let price = '';
            const priceSelectors = [
                '[class*="price"]', '.c-price', '[class*="cost"]',
                'span', 'div', 'strong'
            ];
            for (const sel of priceSelectors) {
                const el = item.querySelector(sel);
                if (el && el.textContent.includes('¥')) {
                    price = el.textContent.trim();
                    break;
                }
            }
            // 如果没找到带¥的，尝试找数字
            if (!price) {
                for (const sel of priceSelectors) {
                    const el = item.querySelector(sel);
                    if (el && /\d+\.?\d*/.test(el.textContent)) {
                        price = el.textContent.trim();
                        break;
                    }
                }
            }
            
            // 提取销量
            let sales = '';
            const salesKeywords = ['月销', '已售', '人付款', '销量', '售出'];
            const allSpans = item.querySelectorAll('span, div');
            for (const el of allSpans) {
                const text = el.textContent;
                if (salesKeywords.some(k => text.includes(k))) {
                    sales = text.trim();
                    break;
                }
            }
            
            // 提取链接
            let url = '';
            const linkEl = item.querySelector('a[href*="item"]') || item.closest('a[href*="item"]');
            if (linkEl) url = linkEl.href;
            
            // 提取item_id
            let itemId = '';
            const idMatch = url.match(/id=(\d+)/);
            if (idMatch) itemId = idMatch[1];
            
            // 去重判断
            const key = itemId || title;
            if (!key || seen.has(key)) continue;
            seen.add(key);
            
            // 只保留有标题和价格的
            if (title && (price || url)) {
                allProducts.push({
                    item_id: itemId,
                    title: title,
                    price: price,
                    sales: sales,
                    url: url,
                    crawl_time: new Date().toLocaleString()
                });
                
                if (allProducts.length <= 10 || allProducts.length % 10 === 0) {
                    console.log(`  ✓ [${allProducts.length}] ${title.substring(0, 35)}... | ${price || '无价格'}`);
                }
            }
        } catch (e) {
            // 静默跳过
        }
    }
    
    console.log(`\n共提取到 ${allProducts.length} 个唯一商品`);
    
    // ====== 第三步：显示结果 ======
    if (allProducts.length === 0) {
        console.log('\n⚠️ 未提取到商品数据');
        console.log('建议手动检查页面结构：');
        console.log('1. 在页面上右键点击一个商品 → 检查');
        console.log('2. 查看该商品外层div的class名');
        console.log('3. 告诉我class名，我可以更新脚本');
        return;
    }
    
    // 显示前10个
    console.log('\n前10个商品预览:');
    for (let i = 0; i < Math.min(10, allProducts.length); i++) {
        const p = allProducts[i];
        console.log(`  ${i+1}. ${p.title.substring(0, 40)}...`);
        console.log(`     价格: ${p.price || '未获取'} | 销量: ${p.sales || '未获取'}`);
    }
    
    // ====== 第四步：数据分析 ======
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
    
    // ====== 第五步：导出文件 ======
    console.log('\n【第五步】导出文件...');
    
    // 导出CSV
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
    a.download = `琢匠_products_${new Date().toISOString().slice(0,10)}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    console.log(`✅ CSV已下载: ${a.download}`);
    
    // 导出JSON
    const jsonBlob = new Blob([JSON.stringify(allProducts, null, 2)], { type: 'application/json' });
    const jsonUrl = URL.createObjectURL(jsonBlob);
    const jsonA = document.createElement('a');
    jsonA.href = jsonUrl;
    jsonA.download = `琢匠_products_${new Date().toISOString().slice(0,10)}.json`;
    document.body.appendChild(jsonA);
    jsonA.click();
    document.body.removeChild(jsonA);
    URL.revokeObjectURL(jsonUrl);
    console.log(`✅ JSON已下载: ${jsonA.download}`);
    
    console.log('\n' + '='.repeat(60));
    console.log('全部完成！');
    console.log('='.repeat(60));
    
})();
