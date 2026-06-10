// background.js - 后台服务

chrome.runtime.onInstalled.addListener(() => {
  console.log('淘宝店铺MHTML保存器已安装');
});

// 监听来自content script的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'saveMHTML') {
    savePageAsMHTML(sender.tab.id, request.filename)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // 保持消息通道开放
  }
});

// 使用Chrome Debugger API保存页面为MHTML
async function savePageAsMHTML(tabId, filename) {
  try {
    // 附加debugger
    await chrome.debugger.attach({ tabId }, '1.3');
    
    // 发送captureSnapshot命令
    const response = await chrome.debugger.sendCommand(
      { tabId },
      'Page.captureSnapshot',
      { format: 'mhtml' }
    );
    
    // 分离debugger
    await chrome.debugger.detach({ tabId });
    
    if (!response.data) {
      throw new Error('MHTML内容为空');
    }
    
    // 创建Blob并下载
    const blob = new Blob([response.data], { type: 'multipart/related' });
    const url = URL.createObjectURL(blob);
    
    const downloadId = await chrome.downloads.download({
      url: url,
      filename: `taobao_products/${filename}`,
      saveAs: false
    });
    
    return { downloadId, filename };
    
  } catch (error) {
    // 确保debugger被分离
    try {
      await chrome.debugger.detach({ tabId });
    } catch (e) {}
    
    throw error;
  }
}

// 监听下载完成
chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state && delta.state.current === 'complete') {
    console.log('下载完成:', delta.id);
  }
});
