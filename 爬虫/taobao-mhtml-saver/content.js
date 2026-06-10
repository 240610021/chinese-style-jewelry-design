// content.js - 内容脚本，在页面中执行

console.log('淘宝店铺MHTML保存器已加载');

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractProducts') {
    const products = extractProductsFromPage();
    sendResponse({ products });
  } else if (request.action === 'scrollPage') {
    scrollPageSimulate().then(() => sendResponse({ done: true }));
    return true;
  }
});

// 提取商品列表
function extractProductsFromPage() {
  const links = document.querySelectorAll('a[href*="item.taobao.com/item.htm"]');
  const products = [];
  const seenIds = new Set();
  
  links.forEach(link => {
    const href = link.getAttribute('href') || '';
    const title = (link.getAttribute('title') || link.textContent || '').trim();
    
    const match = href.match(/id=(\d+)/);
    if (!match) return;
    
    const itemId = match[1];
    if (seenIds.has(itemId)) return;
    seenIds.add(itemId);
    
    if (!title || title.length < 3) return;
    if (['消费者保障', '保证金', '收藏店铺', '装修', '定金'].some(k => title.includes(k))) return;
    
    let url = href;
    if (url.startsWith('//')) url = 'https:' + url;
    
    products.push({ itemId, title, url });
  });
  
  console.log(`提取到 ${products.length} 个商品`);
  return products;
}

// 模拟人类滚动
function scrollPageSimulate() {
  return new Promise(resolve => {
    let count = 0;
    const maxScrolls = 5;
    
    const interval = setInterval(() => {
      // 随机滚动距离（模拟人类不规律的滚动）
      const scrollDistance = 300 + Math.random() * 500;
      window.scrollBy(0, scrollDistance);
      count++;
      
      console.log(`滚动 ${count}/${maxScrolls}`);
      
      if (count >= maxScrolls) {
        clearInterval(interval);
        // 滚动回顶部
        window.scrollTo(0, 0);
        resolve();
      }
    }, 500 + Math.random() * 1000); // 随机间隔
  });
}

// 页面加载完成后自动提取商品（用于调试）
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成，准备提取商品');
  });
}
