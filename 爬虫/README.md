# 淘宝/天猫数据爬虫工具包

> 用于抓取琢匠等竞品店铺的商品信息和用户评价，支持后续数据分析和差评挖掘。

---

## 文件说明

| 文件 | 功能 | 输出 |
|------|------|------|
| `save_taobao_products_mhtml.py` | **自动保存店铺所有商品详情页为MHTML**（推荐） | `.mhtml` 文件 |
| `config_mhtml.py` | MHTML保存工具的配置文件 | - |
| `taobao_shop_selenium.py` | 抓取店铺商品列表（标题、价格、销量） | CSV + JSON |
| `taobao_product_spider.py` | 抓取店铺商品列表（requests版） | CSV + JSON |
| `taobao_review_spider.py` | 抓取单个商品的评价内容 | CSV + JSON |
| `get_cookie.py` | 自动获取淘宝Cookie | `taobao_cookie.txt` |
| `get_cookie_simple.py` | 手动格式化Cookie工具 | `taobao_cookie.txt` |
| `parse_mhtml_batch.py` | 批量解析MHTML文件提取数据 | CSV + JSON |
| `parse_mhtml_product.py` | 解析单个MHTML文件 | JSON |
| `parse_html_products.py` | 解析本地HTML文件提取商品 | CSV + JSON |
| `requirements.txt` | Python依赖包清单 | - |
| `README.md` | 使用说明 | - |

---

## 安装依赖

```bash
pip install -r requirements.txt
```

---

## 使用步骤

### 第一步：获取Cookie（三种方法）

#### 方法A：一键自动获取（推荐，最简单）

```bash
python get_cookie.py
```

1. 运行脚本，自动打开Chrome浏览器
2. 手动登录淘宝
3. 回到命令行窗口按回车
4. Cookie自动复制到剪贴板

#### 方法B：手动复制 + 格式化工具

```bash
python get_cookie_simple.py
```

1. 用Chrome打开淘宝并登录
2. 按 `F12` → 点击 `Console`（控制台）
3. 粘贴代码 `document.cookie` 并按回车
4. 复制输出的长字符串
5. 运行 `get_cookie_simple.py`，粘贴并按回车
6. Cookie自动格式化并保存到文件

#### 方法C：传统手动方法（备用）

1. 打开Chrome浏览器，登录淘宝/天猫
2. 按 `F12` 打开开发者工具
3. 切换到 `Network`（网络）标签
4. 刷新页面，点击任意一个请求
5. 在右侧找到 `Headers` → `Request Headers` → `cookie`
6. 复制完整的Cookie字符串
7. 粘贴到脚本中的 `HEADERS["Cookie"]` 位置

### 第二步：确认目标（已预配置琢匠信息）

**商品爬虫已配置：**
- 店铺：琢匠淘宝主店 `https://shop113403298.taobao.com/`
- 备用：琢匠天猫旗舰店 `https://shop319061276.taobao.com/`

**评价爬虫建议抓取爆款：**
| 商品 | 价格 | 抓取目的 |
|------|------|----------|
| 山鬼剑狮吊坠（铜款） | ¥159 | 天猫爆款，看好评关键词 |
| 饕餮纹手镯（s925银款） | ¥2098 | 高端款，看品控/售后评价 |
| 背云三通文玩配饰 | ¥26起 | 低价款，看差评原因 |
| 虎啸三通配饰（925银） | ¥98 | 文玩配件，看材质反馈 |

获取商品ID方法：打开商品详情页 → 复制URL中 `id=123456789` 的数字部分

### 第三步：运行脚本

**保存商品详情页为MHTML（推荐，效果等同浏览器"另存为"）：**
```bash
python save_taobao_products_mhtml.py
```
1. 运行脚本，自动打开Chrome浏览器
2. 在浏览器中手动登录淘宝
3. 登录完成后按回车，脚本自动开始保存
4. 保存过程中会自动滚动页面、模拟人类浏览行为
5. 支持断点续传，中断后重新运行会跳过已保存商品

**抓取商品列表（Selenium版）：**
```bash
python taobao_shop_selenium.py
```

**抓取商品列表（requests版）：**
```bash
python taobao_product_spider.py
```

**抓取商品评价：**
```bash
python taobao_review_spider.py
```

**解析已保存的MHTML文件：**
```bash
python parse_mhtml_batch.py
```

---

## 注意事项

### 1. 反爬机制
- 淘宝有严格的反爬机制，**务必控制请求频率**
- 脚本已设置随机延迟（2-8秒），不要修改得太低
- 建议使用代理池轮换IP

### 2. 法律风险
- 本脚本仅供学习研究使用
- 抓取数据请勿用于商业竞争或公开传播
- 遵守淘宝 robots.txt 和相关法律法规

### 3. 数据限制
- 淘宝评价默认只显示最近180天的数据
- 部分评价可能被折叠或隐藏
- 销量数据可能是"月销"或"总销"，需注意区分

### 4. 常见问题

| 问题 | 解决方案 |
|------|----------|
| 提示"请登录" | Cookie过期，重新获取Cookie |
| 抓取不到数据 | 检查商品ID/店铺URL是否正确 |
| 页面结构变化 | 需要更新CSS选择器 |
| 被封IP | 使用代理池，降低请求频率 |

---

## 数据分析建议

抓取到数据后，可以进行以下分析：

### 商品分析
- 价格带分布
- 销量TOP10商品
- 新品上架频率
- 价格变动趋势

### 评价分析
- 好评/中评/差评比例
- 差评关键词提取（品控、售后、物流、设计）
- 用户痛点挖掘
- 竞品优势提炼

### 工具推荐
- Excel / WPS：基础数据透视
- Python pandas：数据处理
- Python jieba：中文分词
- Python wordcloud：词云生成

---

> 免责声明：本工具仅供学习研究使用，使用者需自行承担法律责任。
