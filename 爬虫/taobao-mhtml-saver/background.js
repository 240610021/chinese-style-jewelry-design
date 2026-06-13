// background.js - 后台服务

let downloadCount = 0;
let totalDownloads = 0;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'saveMHTML') {
    handleMHTMLSave(message, sender, sendResponse);
    return true;
  }
  
  if (message.action === 'folderSelected') {
    // 通知 popup 更新
    chrome.runtime.sendMessage(message).catch(() => {});
    sendResponse({ ok: true });
    return false;
  }
  
  if (message.action === 'openDownloads') {
    chrome.downloads.showDefaultFolder();
    sendResponse({ ok: true });
    return false;
  }
  
  if (message.action === 'getInfo') {
    sendResponse({ downloadCount, totalDownloads });
    return false;
  }
});

async function handleMHTMLSave(message, sender, sendResponse) {
  try {
    const { filename, data, saveTo } = message;
    
    // 生成 Blob 并下载
    const blob = new Blob([data], { type: 'multipart/related' });
    const url = URL.createObjectURL(blob);
    
    // 使用 downloads API
    chrome.downloads.download({
      url: url,
      filename: filename,
      conflictAction: 'uniquify'
    }, (downloadId) => {
      if (chrome.runtime.lastError) {
        sendResponse({ success: false, error: chrome.runtime.lastError.message });
      } else {
        sendResponse({ success: true, downloadId });
      }
    });
    
  } catch (e) {
    sendResponse({ success: false, error: e.message });
  }
}

chrome.downloads.onChanged.addListener((delta) => {
  if (delta.state && delta.state.current === 'complete') {
    downloadCount++;
    console.log('下载完成:', delta.id, '完成数:', downloadCount);
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log('淘宝店铺MHTML保存器已安装');
});