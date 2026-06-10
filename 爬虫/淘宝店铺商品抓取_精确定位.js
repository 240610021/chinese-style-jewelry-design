/**
 * 淘宝店铺商品抓取脚本（精确定位版）
 * 针对淘宝店铺搜索页的商品卡片结构优化
 * 
 * 使用方法：
 * 1. 用Chrome打开：https://shop113403298.taobao.com/search.htm
 * 2. 确保已登录，页面已加载商品列表
 * 3. 按F12 → Console
 * 4. 复制本代码全部内容，粘贴到Console，按回车
 */

(async function() {
    'use strict';
    
    console.log('='.repeat(60));
    console.log('淘宝店铺商品抓取 - 琢匠（精确定位版）');
    console.log('='.repeat(60));
    
    // ====== 精确定位策略 ======
    // 淘宝店铺商品卡片特征：
    // 1. 包含商品图片 (img)
    // 2. 包含价格 (¥)
    // 3. 包含商品链接 (item.htm)
    // 4. 有明确的标题文本
    
    function isProductCard(element) {
        // 必须有商品链接
        const hasItemLink = element.querySelector('a[href*="item.htm"]') !== null;
        if (!hasItemLink) return false;
        
        // 必须有图片
        const hasImage = element.querySelector('img') !== null;
        if (!hasImage) return false;
        
        // 必须有价格（包含¥或数字）
        const text = element.textContent;
        const hasPrice = text.includes('¥') || /\d+\.\d{2}/.test(text);
        if (!hasPrice) return false;
        
        // 排除非商品元素（通过关键词过滤）
        const excludeKeywords = ['消费者保障', '保证金', '收藏店铺', '装修此页面', '品质工厂', '所有分类'];
        const titleEl = element.querySelector('a[title], [class*="title"]');
        const titleText = titleEl ? (titleEl.getAttribute('title') || titleEl.textContent) : text;
        
        for (const keyword of excludeKeywords) {
            if (titleText.includes(keyword)) return false;
        }
        
        // 尺寸检查（商品卡片通常有一定大小）
        const rect = element.getBoundingClientRect();
        if (rect.width < 80 || rect.height < 80) return false;
        
        return true;
    }
    
    // ====== 寻找商品卡片 ======
    console.log('\n【第一步】寻找商品卡片...');
    
    // 策略1：找包含item链接的a标签，然后向上找父容器
    const itemLinks = document.querySelectorAll('a[href*="item.htm"]');
    console.log(`找到 ${itemLinks.length} 个商品链接`);
    
    const productCards = [];
    const seen = new Set();
    
    for (const link of itemLinks) {
        // 向上查找3层，找到合适的容器
        let card = link;
        for (let i = 0; i < 4; i++) {
            if (!card.parentElement) break;
            card = card.parentElement;
            
            if (isProductCard(card)) {
                const id = card.querySelector('a[href*="item.htm"]')?.href?.match(/id=(\d+)/)?.[1];
                if (id && !seen.has(id)) {
                    seen.add(id);
                    productCards.push(card);
                }
                break;
            }
        }
    }
    
    console.log(`筛选后得到 ${productCards.length} 个商品卡片`);
    
    if (productCards.length === 0) {
        console.log('\n⚠️ 未找到商品卡片');
        console.log('请确保：');
        console.log('1. 当前页面是店铺搜索页（URL包含 search.htm）');
        console.log('2. 页面已加载完成，能看到商品列表');
        console.log('3. 已登录淘宝账号');
        return;
    }
    
    // ====== 提取商品数据 ======
    console.log('\n【第二步】提取商品数据...');
    
    const allProducts = [];
    
    for (let i = 0; i < productCards.length; i++) {
        const card = productCards[i];
        
        try {
            // 提取item_id和URL
            const linkEl = card.querySelector('a[href*="item.htm"]');
            const url = linkEl ? linkEl.href : '';
            const itemId = url.match(/id=(\d+)/)?.[1] || '';
            
            // 提取标题
            let title = '';
            // 优先从a标签的title属性获取
            if (linkEl && linkEl.getAttribute('title')) {
                title = linkEl.getAttribute('title').trim();
            }
            // 其次从img的alt获取
            if (!title) {
                const img = card.querySelector('img');
                if (img && img.alt) {
                    title = img.alt.trim();
                }
            }
            // 最后从文本内容获取
            if (!title) {
                const textEls = card.querySelectorAll('span, div, a');
                for (const el of textEls) {
                    const text = el.textContent.trim();
                    if (text.length > 10 && !text.includes('¥') && !text.includes('销量')) {
                        title = text;
                        break;
                    }
                }
            }
            
            // 提取价格 - 找包含¥的元素
            let price = '';
            const allElements = card.querySelectorAll('*');
            for (const el of allElements) {
                const text = el.textContent.trim();
                if (text.startsWith('¥') && /¥\d+/.test(text)) {
                    price = text;
                    break;
                }
            }
            // 如果没找到带¥的，找纯数字价格
            if (!price) {
                for (const el of allElements) {
                    const text = el.textContent.trim();
                    if (/^\d+\.\d{2}$/.test(text)) {
                        price = '¥' + text;
                        break;
                    }
                }
            }
            
            // 提取销量
            let sales = '';
            const salesKeywords = ['月销', '已售', '人付款', '销量', '售出', '付款'];
            for (const el of allElements) {
                const text = el.textContent.trim();
                if (salesKeywords.some(k => text.includes(k)) && /\d+/.test(text)) {
                    sales = text;
                    break;
                }
            }
            
            // 提取店铺名
            let shopName = '';
            const shopEl = card.querySelector('[class*="shop"]');
            if (shopEl) {
                shopName = shopEl.textContent.trim();
            }
            
            // 提取图片URL
            let imgUrl = '';
            const img = card.querySelector('img');
            if (img) {
                imgUrl = img.src || img.getAttribute('data-src') || '';
            }
            
            // 过滤无效数据
            if (!title || title.length < 5) continue;
            if (!price && !itemId) continue;
            
            // 排除非商品
            const excludeKeywords = ['消费者保障', '保证金', '收藏店铺', '装修', '品质工厂', '所有分类', '首页'];
            if (excludeKeywords.some(k => title.includes(k))) continue;
            
            allProducts.push({
                item_id: itemId,
                title: title,
                price: price,
                sales: sales,
                shop_name: shopName,
                img_url: imgUrl,
                url: url,
                crawl_time: new Date().toLocaleString()
            });
            
            if (allProducts.length <= 10 || allProducts.length % 10 === 0) {
                console.log(`  ✓ [${allProducts.length}] ${title.substring(0, 35)}... | ${price || '无价格'}`);
            }
            
        } catch (e) {
            // 静默跳过
        }
    }
    
    console.log(`\n共提取到 ${allProducts.length} 个有效商品`);
    
    // ====== 显示结果 ======
    if (allProducts.length === 0) {
        console.log('\n⚠️ 未提取到有效商品数据');
        return;
    }
    
    // 显示前10个
    console.log('\n前10个商品预览:');
    for (let i = 0; i < Math.min(10, allProducts.length); i++) {
        const p = allProducts[i];
        console.log(`  ${i+1}. ${p.title.substring(0, 40)}...`);
        console.log(`     价格: ${p.price || '未获取'} | 销量: ${p.sales || '未获取'}`);
    }
    
    // ====== 数据分析 ======
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
    
    // ====== 导出文件 ======
    console.log('\n【第三步】导出文件...');
    
    // 导出CSV
    const headers = Object.keys(allProducts[0]);
    const csvContent = [
        headers.join(','),
        ...allProducts.map(p => headers.map(h => {
            const val = p[h] || '';
            if (typeof val === 'string' && (val.includes(',') || val.includes('"') || val.includes('\n'))) {
                return `"${val.replace(/"/g, '""').replace(/\n/g, ' ')}"`;
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
