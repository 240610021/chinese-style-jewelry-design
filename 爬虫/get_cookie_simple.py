#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝Cookie获取工具（简化版）
无需Selenium，手动复制Cookie后自动格式化
"""

import re


def format_cookie():
    """格式化Cookie"""
    print("=" * 60)
    print("淘宝Cookie格式化工具")
    print("=" * 60)
    print("\n使用方法：")
    print("1. 用Chrome打开淘宝并登录")
    print("2. 按F12 → 点击Console（控制台）")
    print("3. 粘贴以下代码并按回车：")
    print("-" * 60)
    print("document.cookie")
    print("-" * 60)
    print("4. 复制输出的长字符串")
    print("5. 回到此窗口，粘贴并按回车\n")
    
    # 获取用户输入
    raw_cookie = input("请粘贴Cookie字符串: ").strip()
    
    if not raw_cookie:
        print("未输入Cookie")
        return
    
    # 清理和格式化
    # 去除可能的引号
    cookie = raw_cookie.strip('"').strip("'")
    
    # 确保格式正确（分号分隔）
    if ';' not in cookie:
        print("⚠️ 警告：Cookie中未找到分号，可能格式不正确")
    
    # 保存到文件
    with open("taobao_cookie.txt", "w", encoding="utf-8") as f:
        f.write(cookie)
    
    print("\n" + "=" * 60)
    print("✅ Cookie已格式化并保存！")
    print("=" * 60)
    print(f"\n长度: {len(cookie)} 字符")
    print(f"\n文件已保存: taobao_cookie.txt")
    print("\n请打开爬虫脚本，将以下内容粘贴到 Cookie 字段：")
    print("-" * 60)
    print(cookie[:200] + "..." if len(cookie) > 200 else cookie)
    print("-" * 60)
    
    return cookie


def main():
    """主函数"""
    format_cookie()
    input("\n按回车键退出...")


if __name__ == "__main__":
    main()
