#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝Cookie一键获取工具
功能：自动打开Chrome浏览器，登录淘宝后一键复制Cookie到剪贴板
使用方法：
1. 运行脚本
2. 在打开的浏览器中登录淘宝
3. 按提示按回车键
4. Cookie自动复制到剪贴板，直接粘贴到爬虫脚本中即可
"""

import time
import json
import subprocess
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    print("请先安装依赖: pip install selenium webdriver-manager")
    sys.exit(1)

def get_cookie():
    """获取淘宝Cookie"""
    print("=" * 60)
    print("淘宝Cookie一键获取工具")
    print("=" * 60)
    print("\n步骤：")
    print("1. 即将自动打开Chrome浏览器并跳转淘宝登录页")
    print("2. 请手动登录淘宝账号")
    print("3. 登录成功后，回到此窗口按回车键")
    print("4. Cookie将自动复制到剪贴板")
    print("=" * 60)
    
    input("\n按回车键开始...")
    
    # 配置Chrome选项
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 取消注释可无头模式（不显示窗口）
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1200,800")
    chrome_options.add_argument("--no-sandbox")
    
    print("\n正在启动浏览器...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 打开淘宝登录页
        driver.get("https://login.taobao.com/")
        print("已打开淘宝登录页，请手动登录...")
        
        # 等待用户登录
        input("\n登录完成后，请按回车键获取Cookie...")
        
        # 获取Cookie
        cookies = driver.get_cookies()
        
        # 转换为请求头格式的Cookie字符串
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        # 复制到剪贴板
        try:
            import pyperclip
            pyperclip.copy(cookie_str)
            print("\n✅ Cookie已复制到剪贴板！")
        except ImportError:
            print("\n⚠️ 未安装pyperclip，Cookie将输出到下方，请手动复制：")
            print("=" * 60)
            print(cookie_str)
            print("=" * 60)
        
        # 同时保存为文件
        with open("taobao_cookie.txt", "w", encoding="utf-8") as f:
            f.write(cookie_str)
        print("\nCookie也已保存到: taobao_cookie.txt")
        
        # 显示Cookie信息
        print(f"\nCookie长度: {len(cookie_str)} 字符")
        print(f"包含 {len(cookies)} 个Cookie项")
        print("\n主要Cookie项:")
        for c in cookies[:10]:  # 只显示前10个
            value = c['value'][:30] + "..." if len(c['value']) > 30 else c['value']
            print(f"  {c['name']}: {value}")
        
        return cookie_str
        
    finally:
        driver.quit()
        print("\n浏览器已关闭")


def main():
    """主函数"""
    cookie = get_cookie()
    
    print("\n" + "=" * 60)
    print("使用说明：")
    print("=" * 60)
    print("1. 打开 taobao_product_spider.py 或 taobao_review_spider.py")
    print("2. 找到 HEADERS 中的 'Cookie' 字段")
    print("3. 将剪贴板中的内容粘贴替换 '你的Cookie字符串'")
    print("4. 保存文件，运行爬虫脚本")
    print("=" * 60)
    
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
