/**
 * 淘宝店铺页面保存工具
 * 功能：自动翻页，将每一页保存为本地HTML文件
 * 使用方法：
 * 1. 用Chrome打开：https://shop113403298.taobao.com/search.htm
 * 2. 确保已登录，页面已加载
 * 3. 按F12 → Console
 * 4. 复制本代码，粘贴执行
 * 5. 脚本会自动翻页并下载每一页的HTML
 */

(async function() {
    'use strict';
    
    const SHOP_NAME = "琢匠";
    const MAX_PAGES = 50;  // 最大翻页数
    const WAIT_TIME = 3000;  // 每页等待时间（毫秒）
    
    console.log('='.repeat(60));
    console.log('淘宝店铺页面保存工具');
    console.log('='.repeat(60));
    console.log('将自动翻页并保存每一页为HTML文件');
    console.log('保存位置：浏览器下载文件夹');
    console.log('='.repeat(60));
    
    let currentPage = 1;
    
    // 获取当前页码
    function getCurrentPage() {
        const urlParams = new URLSearchParams(window.location.search);
        const page = urlParams.get('pageNo') || urlParams.get('page') || '1';
        return parseInt(page);
    }
    
    // 保存当前页面HTML
    function saveCurrentPage() {
        const html = document.documentElement.outerHTML;
        const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `${SHOP_NAME}_page_${String(currentPage).padStart(3, '0')}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log(`✅ 已保存第 ${currentPage} 页: ${a.download}`);
    }
    
    // 点击下一页
    async function clickNextPage() {
        // 尝试多种下一页按钮
        const nextSelectors = [
            '.next:not(.disabled)',
            '.pagination-next',
            'a[title="下一页"]',
            'button:contains("下一页")',
            '.page-next',
            '[class*="next"]:not([class*="disabled"])'
        ];
        
        for (const selector of nextSelectors) {
            try {
                const nextBtn = document.querySelector(selector);
                if (nextBtn && !nextBtn.disabled && !nextBtn.classList.contains('disabled')) {
                    nextBtn.click();
                    return true;
                }
            } catch (e) {}
        }
        
        // 尝试通过URL参数翻页
        const currentUrl = new URL(window.location.href);
        const currentPageNo = parseInt(currentUrl.searchParams.get('pageNo') || '1');
        currentUrl.searchParams.set('pageNo', currentPageNo + 1);
        
        console.log(`尝试通过URL翻页到第 ${currentPageNo + 1} 页...`);
        window.location.href = currentUrl.toString();
        return true;
    }
    
    // 主循环
    for (let i = 0; i < MAX_PAGES; i++) {
        console.log(`\n正在处理第 ${currentPage} 页...`);
        
        // 等待页面加载
        await new Promise(r => setTimeout(r, WAIT_TIME));
        
        // 滚动加载所有商品
        console.log('滚动加载商品...');
        for (let j = 0; j < 5; j++) {
            window.scrollTo(0, document.body.scrollHeight);
            await new Promise(r => setTimeout(r, 1000));
        }
        
        // 保存当前页
        saveCurrentPage();
        
        // 检查是否有下一页
        const hasNext = document.querySelector('.next:not(.disabled), .pagination-next, a[title="下一页"]');
        if (!hasNext) {
            console.log('\n没有下一页了，抓取完成！');
            break;
        }
        
        // 点击下一页
        console.log('点击下一页...');
        const success = await clickNextPage();
        if (!success) {
            console.log('无法翻页，可能已到达末尾');
            break;
        }
        
        currentPage++;
        
        // 等待新页面加载
        await new Promise(r => setTimeout(r, WAIT_TIME));
    }
    
    console.log('\n' + '='.repeat(60));
    console.log('全部完成！');
    console.log(`共保存 ${currentPage} 页HTML`);
    console.log('文件保存在浏览器的下载文件夹中');
    console.log('='.repeat(60));
    
})();
