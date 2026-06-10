#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHTML 保存配置文件
修改此文件即可切换目标店铺和参数
"""

import os

# ============ 目标店铺配置 ============

SHOP_NAME = "CoppertistWu"  # 店铺名称（用于文件名和输出）
SHOP_SEARCH_URL = "https://coppertistwu.jiyoujia.com/search.htm"  # 店铺搜索页URL

# ============ 输出配置 ============

# 输出目录（保存MHTML文件的文件夹）
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "新建文件夹")

# 进度文件路径（记录已保存的商品，支持断点续传）
PROGRESS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_mhtml_progress.json")

# ============ 浏览器配置 ============

# QQ浏览器路径（已自动检测到）
BROWSER_EXE = r"C:\Program Files\Tencent\QQBrowser\QQBrowser.exe"

# 浏览器用户数据目录（QQ浏览器的，复用登录状态）
BROWSER_USER_DATA = r"C:\Users\Administrator\AppData\Local\Tencent\QQBrowser\User Data"

# 远程调试端口
REMOTE_DEBUGGING_PORT = 9222

# Chrome驱动路径（可选，自动检测）
CHROMEDRIVER_PATH = None

# ============ 反爬/模拟人类配置 ============

# 每次操作间的随机延迟范围（秒）
# 模拟人类操作节奏，降低反爬风险
MIN_DELAY = 3
MAX_DELAY = 8

# 页面加载后的等待时间（秒）
PAGE_LOAD_WAIT = 3

# 页面滚动次数（模拟人类向下滚动浏览）
SCROLL_TIMES = 5

# 每次滚动后的等待时间（秒）
SCROLL_DELAY = 2

# 最大翻页数
MAX_PAGES = 50

# 网络超时重试次数
MAX_RETRIES = 3

# 显式等待超时时间（秒）
EXPLICIT_WAIT_TIMEOUT = 15

# ============ 文件名配置 ============

# MHTML文件名格式模板
# 可用变量: {title} 商品标题, {item_id} 商品ID
FILENAME_TEMPLATE = "{title}_{item_id}-淘宝网.mhtml"

# 文件名中需要替换的非法字符
ILLEGAL_CHARS = r'[\/:*?"<>|]'

# 文件名最大长度（超出则截断标题）
MAX_FILENAME_LENGTH = 200
