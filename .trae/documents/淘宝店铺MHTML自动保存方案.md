# 淘宝商家店铺产品自动保存为 MHTML — 实施计划

## 摘要

基于现有爬虫项目，创建一个**模拟人类操作**的自动化脚本，将淘宝商家店铺的所有商品详情页**保存为 MHTML 格式**（与浏览器"另存为网页，单一文件"效果一致）。目标店铺为"琢匠"，最终保存的 MHTML 文件用于后续数据分析。

## 现状分析

### 已有资源
- **Selenium方案**: `taobao_shop_selenium.py` — 可抓取店铺商品列表，但不保存 MHTML
- **Cookie获取**: `get_cookie.py` / `get_cookie_simple.py` — 可获取登录 Cookie
- **MHTML解析**: `parse_mhtml_batch.py` / `parse_mhtml_product.py` — 可解析已保存的 MHTML 文件
- **已有数据**: `新建文件夹/` 下有约40个已保存的 `.mhtml` 商品详情页

### 核心问题
1. **没有"保存为 MHTML"的自动化脚本** — 现有脚本只抓取列表数据，不逐个访问并保存 MHTML
2. **MHTML 与 HTML 的区别**: MHTML 是将网页所有资源（HTML、CSS、图片、JS）打包成单一文件，离线可完整查看；HTML 只是源码，图片等资源仍指向线上地址

## 技术方案

### 核心方法：Chrome DevTools Protocol — `Page.captureSnapshot`

Selenium 可以通过 `driver.execute_cdp_cmd('Page.captureSnapshot', {})` 直接获取页面的 MHTML 内容，效果等同于浏览器"另存为 → 网页，单一文件"。[1]

```python
res = driver.execute_cdp_cmd('Page.captureSnapshot', {})
mhtml_content = res['data']
with open('product.mhtml', 'w', newline='') as f:
    f.write(mhtml_content)
```

### 方案对比

| 方法 | 原理 | 优点 | 缺点 |
|------|------|------|------|
| **CDP `Page.captureSnapshot`** | Chrome DevTools 原生命令 | 代码简洁，无需模拟键盘操作，资源打包完整 | 需确保页面完全加载 |
| 模拟 Ctrl+S + 选择格式 | 模拟人类键盘操作 | 最接近人类操作 | 依赖系统对话框，不稳定 |
| `page_source` + 手动下载资源 | 获取 HTML 后手动下载图片/CSS | 可控性强 | 代码复杂，资源处理繁琐 |

**选择：CDP `Page.captureSnapshot`** — 最稳定、最简洁，效果与浏览器"另存为"完全一致。

## 实施步骤

### 步骤1：创建主脚本 `save_taobao_products_mhtml.py`

**文件**: `g:\Downloads\蔡规划\爬虫\save_taobao_products_mhtml.py`

**功能流程**（模拟人类操作）：
1. 启动 Chrome 浏览器（带反检测配置）
2. 打开淘宝登录页，等待用户手动登录
3. 导航到目标店铺的商品列表页
4. **模拟人类浏览行为**：
   - 自动滚动页面加载商品（像人类一样向下滚动）
   - 等待页面稳定（随机延迟 2-5 秒）
5. 提取所有商品链接和标题
6. **逐个访问商品详情页**（模拟人类点击商品）：
   - 打开商品详情页
   - 等待页面完全渲染（等待关键元素出现）
   - **模拟人类浏览**：滚动查看商品详情
   - 使用 `Page.captureSnapshot` 保存为 MHTML
   - 文件名格式：`{商品标题}_{商品ID}-淘宝网.mhtml`
   - 保存到指定目录（默认 `g:\Downloads\蔡规划\新建文件夹\`）
7. 每次操作间随机延迟（3-8 秒），模拟人类操作节奏
8. 记录已保存商品 ID，支持断点续传
9. 完成后输出汇总报告

**关键实现细节**:
- 反检测配置：隐藏 `navigator.webdriver`，排除自动化开关
- 文件名清理：去除标题中的特殊字符（`/`、`\`、`:`、`*`、`?`、`"`、`<`、`>`、`|`）
- 进度显示：当前商品序号/总数、商品标题、耗时
- 异常处理：网络超时重试（最多3次）、跳过无效页面
- 保存进度文件 `saved_mhtml_progress.json`
- 页面加载等待：使用显式等待（`WebDriverWait`）而非固定 `time.sleep`

### 步骤2：创建配置文件 `config_mhtml.py`

**文件**: `g:\Downloads\蔡规划\爬虫\config_mhtml.py`

**内容**:
- 目标店铺 URL/店铺 ID
- 输出目录路径
- 请求延迟范围（秒）
- 最大翻页数
- 最大重试次数
- Chrome 驱动路径（可选）

### 步骤3：更新 `requirements.txt`

**变更**:
- 移除未使用的依赖：`pandas`、`openpyxl`
- 确认已有依赖版本号合理
- 添加 `pyperclip`（可选依赖）

### 步骤4：更新 `README.md`

补充新脚本 `save_taobao_products_mhtml.py` 的使用说明。

## 假设与决策

| 决策 | 理由 |
|------|------|
| 使用 CDP `Page.captureSnapshot` | 最稳定，效果等同于浏览器"另存为"，代码简洁 [1] |
| 保存为 MHTML 而非 HTML | MHTML 将所有资源打包为单一文件，离线可完整查看 |
| 手动登录而非 Cookie 复用 | Cookie 有效期短，手动登录最稳定 |
| 逐个访问详情页 | 淘宝 API 需企业认证，详情页内容最完整 |
| 随机延迟 3-8 秒 | 模拟人类操作节奏，降低反爬风险 |
| 使用显式等待 | 比固定 `time.sleep` 更高效，页面加载完成即可继续 |

## 验证步骤

1. 运行脚本，确认能启动 Chrome 并打开淘宝
2. 手动登录后，确认能正确提取店铺商品列表
3. 确认能逐个访问商品详情页并保存 MHTML
4. 检查保存的 MHTML 文件是否完整（用浏览器打开，确认图片、样式正常）
5. 用现有的 `parse_mhtml_batch.py` 验证能否正确解析保存的 MHTML
6. 测试断点续传：中断后重新运行，确认跳过已保存商品
7. 测试异常处理：断网、超时、页面 404 等场景

## Sources

1. [使用selenium将网页保存为MHTML格式 - CSDN](https://blog.csdn.net/qq_46311811/article/details/128632254)
