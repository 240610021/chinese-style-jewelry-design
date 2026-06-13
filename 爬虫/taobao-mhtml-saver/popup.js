// popup.js - 插件弹窗逻辑

let isRunning = false;
let productList = [];

// 获取DOM元素
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const exportBtn = document.getElementById('exportBtn');
const selectFolderBtn = document.getElementById('selectFolderBtn');
const saveFolderInput = document.getElementById('saveFolder');
const statusDiv = document.getElementById('status');
const progressSection = document.getElementById('progressSection');
const currentSpan = document.getElementById('current');
const totalSpan = document.getElementById('total');
const progressBar = document.getElementById('progressBar');
const currentItemSpan = document.getElementById('currentItem');
const logDiv = document.getElementById('log');
const delayInput = document.getElementById('delayMin');
const maxItemsInput = document.getElementById('maxItems');

// 加载上次保存的路径，并监听变化
function loadSavePath() {
  chrome.storage.local.get(['savePath', 'selectedFolder'], (result) => {
    if (result.selectedFolder) {
      saveFolderInput.value = result.selectedFolder;
    } else if (result.savePath) {
      saveFolderInput.value = result.savePath;
    }
  });
}
loadSavePath();

// 每秒刷新一次（检测picker传来的选择结果）
setInterval(loadSavePath, 1000);

// 浏览按钮 - 在新标签页中打开文件夹选择器
selectFolderBtn.addEventListener('click', () => {
  // 方案1：尝试在弹窗中直接使用 showDirectoryPicker
  if (typeof showDirectoryPicker === 'function') {
    tryShowDirectoryPicker();
    return;
  }
  
  // 方案2：打开 picker.html 页面来选择文件夹
  const pickerUrl = chrome.runtime.getURL('picker.html');
  chrome.tabs.create({ url: pickerUrl, active: true }, (tab) => {
    addLog('已打开文件夹选择器，选择后回到这里');
  });
});

// 尝试在弹窗中调用 showDirectoryPicker
async function tryShowDirectoryPicker() {
  try {
    addLog('正在打开文件夹选择对话框...');
    const handle = await showDirectoryPicker({ mode: 'readwrite' });
    saveFolderInput.value = handle.name;
    chrome.storage.local.set({ savePath: handle.name, folderSelected: true });
    addLog('✅ 已选择文件夹: ' + handle.name);
    updateStatus('已选择文件夹: ' + handle.name, 'completed');
  } catch (err) {
    if (err.name === 'AbortError') {
      addLog('已取消选择');
    } else {
      addLog('选择失败: ' + err.message);
      // 回退到手动输入
      showPathPrompt();
    }
  }
}

// 手动输入路径的对话框
function showPathPrompt() {
  const msg = '📂 获取文件夹路径：\n\n'
    + '1. 打开文件资源管理器，找到目标文件夹\n'
    + '2. 点击地址栏 → Ctrl+A → Ctrl+C 复制路径\n'
    + '3. 粘贴到下方：';
  const path = prompt(msg, saveFolderInput.value || 'G:\\Downloads\\蔡规划\\新建文件夹');
  if (path) {
    saveFolderInput.value = path.trim().replace(/\\\\/g, '/').replace(/\\/g, '/');
    chrome.storage.local.set({ savePath: saveFolderInput.value });
    addLog('✅ 已设置: ' + saveFolderInput.value);
  }
}

// 监听来自picker.html的消息
window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'folder-selected') {
    saveFolderInput.value = event.data.name;
    chrome.storage.local.set({ savePath: event.data.name });
    addLog('✅ 已选择文件夹: ' + event.data.name);
  }
});

// 添加日志
function addLog(message) {
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.textContent = '[' + new Date().toLocaleTimeString() + '] ' + message;
  logDiv.insertBefore(entry, logDiv.firstChild);
  while (logDiv.children.length > 20) {
    logDiv.removeChild(logDiv.lastChild);
  }
}

function updateStatus(text, type) {
  statusDiv.textContent = text;
  statusDiv.className = 'status ' + (type || '');
}

function updateProgress(current, total, itemName) {
  currentSpan.textContent = current;
  totalSpan.textContent = total;
  currentItemSpan.textContent = itemName || '-';
  progressBar.style.width = total > 0 ? (current / total * 100) + '%' : '0%';
}

// 开始保存
startBtn.addEventListener('click', async () => {
  if (isRunning) return;
  
  const saveTo = saveFolderInput.value.trim();
  if (!saveTo) {
    updateStatus('请先输入或选择保存文件夹！', 'error');
    return;
  }
  
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
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: extractProducts
    });

    productList = results[0].result || [];
    
    if (productList.length === 0) {
      updateStatus('未找到商品，请确保在店铺搜索页', 'error');
      resetUI();
      return;
    }

    const maxItems = parseInt(maxItemsInput.value) || 100;
    productList = productList.slice(0, maxItems);
    
    updateStatus('找到 ' + productList.length + ' 个商品，开始保存...', 'running');
    addLog('找到 ' + productList.length + ' 个商品');
    updateProgress(0, productList.length, '-');

    const delay = parseInt(delayInput.value) || 3;
    
    for (let i = 0; i < productList.length && isRunning; i++) {
      const product = productList[i];
      updateProgress(i + 1, productList.length, product.title.substring(0, 30));
      addLog('正在保存: ' + product.title.substring(0, 30) + '...');

      const pageData = await openAndCaptureProduct(tab.id, product.url);
      
      if (pageData) {
        const filename = sanitizeFilename(product.title) + '_' + product.itemId + '-淘宝网.mhtml';
        // 直接传给后台保存
        await chrome.runtime.sendMessage({
          action: 'saveMHTML',
          filename: filename,
          data: pageData,
          saveTo: saveTo
        });
        addLog('✅ 已保存: ' + filename.substring(0, 40));
      } else {
        addLog('❌ 无法获取页面内容');
      }
      
      if (i < productList.length - 1 && isRunning) {
        await sleep(delay * 1000);
      }
    }

    if (isRunning) {
      updateStatus('完成！共保存 ' + productList.length + ' 个商品', 'completed');
      addLog('全部保存完成！文件位置: ' + saveTo);
    } else {
      updateStatus('已停止', 'error');
    }
  } catch (e) {
    updateStatus('错误: ' + e.message, 'error');
    addLog('错误: ' + e.message);
  }
  resetUI();
});

function resetUI() {
  isRunning = false;
  startBtn.style.display = 'block';
  stopBtn.style.display = 'none';
}

async function openAndCaptureProduct(tabId, productUrl) {
  try {
    await chrome.tabs.update(tabId, { url: productUrl });
    await sleep(5000);
    await chrome.debugger.attach({ tabId }, '1.3');
    const response = await chrome.debugger.sendCommand({ tabId }, 'Page.captureSnapshot', { format: 'mhtml' });
    await chrome.debugger.detach({ tabId });
    return response.data || null;
  } catch (e) {
    try { await chrome.debugger.detach({ tabId }); } catch (ee) {}
    return null;
  }
}

stopBtn.addEventListener('click', () => {
  isRunning = false;
  updateStatus('正在停止...', 'error');
});

exportBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const results = await chrome.scripting.executeScript({ target: { tabId: tab.id }, func: extractProducts });
  const products = results[0].result || [];
  if (products.length === 0) { updateStatus('未找到商品', 'error'); return; }
  const dataStr = JSON.stringify(products, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
  await chrome.downloads.download({ url: dataUri, filename: 'taobao_products.json' });
  updateStatus('已导出 ' + products.length + ' 个商品', 'completed');
  addLog('已导出商品列表');
});

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

function sanitizeFilename(title) {
  return title.replace(/[\\/:*?"<>|]/g, '_').substring(0, 80);
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}