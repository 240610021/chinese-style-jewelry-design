// popup.js - 插件弹窗逻辑

let isRunning = false;
let productList = [];
let currentIndex = 0;

// 获取DOM元素
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const exportBtn = document.getElementById('exportBtn');
const statusDiv = document.getElementById('status');
const progressSection = document.getElementById('progressSection');
const currentSpan = document.getElementById('current');
const totalSpan = document.getElementById('total');
const progressBar = document.getElementById('progressBar');
const currentItemSpan = document.getElementById('currentItem');
const logDiv = document.getElementById('log');
const delayInput = document.getElementById('delayMin');
const maxItemsInput = document.getElementById('maxItems');

// 添加日志
function addLog(message) {
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
  logDiv.insertBefore(entry, logDiv.firstChild);
  
  // 限制日志数量
  while (logDiv.children.length > 20) {
    logDiv.removeChild(logDiv.lastChild);
  }
}

// 更新状态
function updateStatus(text, type = '') {
  statusDiv.textContent = text;
  statusDiv.className = 'status ' + type;
}

// 更新进度
function updateProgress(current, total, itemName) {
  currentSpan.textContent = current;
  totalSpan.textContent = total;
  currentItemSpan.textContent = itemName || '-';
  const percent = total > 0 ? (current / total * 100) : 0;
  progressBar.style.width = percent + '%';
}

// 开始保存
startBtn.addEventListener('click', async () => {
  if (isRunning) return;
  
  // 获取当前标签页
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  if (!tab.url.includes('taobao.com') && !tab.url.includes('jiyoujia.com')) {
    updateStatus('请先打开淘宝店铺页面！', 'error');
    return;
  }

  isRunning = true;
  startBtn.style.display = 'none';
  stopBtn.style.display = 'block';
  progressSection.style.display = 'block';
  updateStatus('正在提取商品列表...', 'running');
  addLog('开始提取商品...');

  try {
    // 第一步：提取商品列表
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: extractProducts
    });

    productList = results[0].result || [];
    
    if (productList.length === 0) {
      updateStatus('未找到商品，请确保在店铺搜索页', 'error');
      addLog('未找到商品');
      isRunning = false;
      startBtn.style.display = 'block';
      stopBtn.style.display = 'none';
      return;
    }

    const maxItems = parseInt(maxItemsInput.value) || 100;
    productList = productList.slice(0, maxItems);
    
    updateStatus(`找到 ${productList.length} 个商品，开始保存...`, 'running');
    addLog(`找到 ${productList.length} 个商品`);
    updateProgress(0, productList.length, '-');

    // 第二步：逐个保存商品
    const delay = parseInt(delayInput.value) || 3;
    
    for (let i = 0; i < productList.length && isRunning; i++) {
      currentIndex = i;
      const product = productList[i];
      
      updateProgress(i + 1, productList.length, product.title.substring(0, 30));
      addLog(`正在保存: ${product.title.substring(0, 30)}...`);

      // 打开商品页面
      await chrome.tabs.update(tab.id, { url: product.url });
      
      // 等待页面加载
      await sleep(5000);
      
      // 滚动页面（模拟人类浏览）
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: scrollPage
      });
      
      await sleep(2000);
      
      // 保存为MHTML
      const filename = `${sanitizeFilename(product.title)}_${product.itemId}-淘宝网.mhtml`;
      
      try {
        // 使用Chrome的Page.saveAsMhtml API
        const client = await chrome.debugger.attach({ tabId: tab.id }, '1.3');
        const response = await chrome.debugger.sendCommand(
          { tabId: tab.id },
          'Page.captureSnapshot',
          { format: 'mhtml' }
        );
        
        if (response.data) {
          // 下载MHTML内容
          const blob = new Blob([response.data], { type: 'multipart/related' });
          const url = URL.createObjectURL(blob);
          
          await chrome.downloads.download({
            url: url,
            filename: `taobao_products/${filename}`,
            saveAs: false
          });
          
          addLog(`✅ 已保存: ${filename.substring(0, 40)}`);
        }
        
        await chrome.debugger.detach({ tabId: tab.id });
      } catch (e) {
        addLog(`❌ 保存失败: ${e.message}`);
      }
      
      // 延迟
      if (i < productList.length - 1) {
        await sleep(delay * 1000);
      }
    }

    if (isRunning) {
      updateStatus(`完成！共保存 ${productList.length} 个商品`, 'completed');
      addLog('全部保存完成！');
    } else {
      updateStatus('已停止', 'error');
      addLog('用户停止');
    }

  } catch (e) {
    updateStatus(`错误: ${e.message}`, 'error');
    addLog(`错误: ${e.message}`);
  }

  isRunning = false;
  startBtn.style.display = 'block';
  stopBtn.style.display = 'none';
});

// 停止保存
stopBtn.addEventListener('click', () => {
  isRunning = false;
  updateStatus('正在停止...', 'error');
});

// 导出商品列表
exportBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: extractProducts
  });

  const products = results[0].result || [];
  
  if (products.length === 0) {
    updateStatus('未找到商品', 'error');
    return;
  }

  // 导出为JSON
  const dataStr = JSON.stringify(products, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
  
  await chrome.downloads.download({
    url: dataUri,
    filename: 'taobao_products.json',
    saveAs: false
  });
  
  updateStatus(`已导出 ${products.length} 个商品`, 'completed');
  addLog(`已导出商品列表: ${products.length} 个`);
});

// 提取商品列表（在页面中执行）
function extractProducts() {
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
  
  return products;
}

// 滚动页面（在页面中执行）
function scrollPage() {
  return new Promise(resolve => {
    let count = 0;
    const interval = setInterval(() => {
      window.scrollBy(0, 500);
      count++;
      if (count >= 5) {
        clearInterval(interval);
        window.scrollTo(0, 0);
        resolve();
      }
    }, 500);
  });
}

// 清理文件名
function sanitizeFilename(title) {
  return title.replace(/[\\/:*?"<>|]/g, '_').substring(0, 80);
}

// 睡眠函数
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
