#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝店铺MHTML保存器 - 图形界面版
特点：
1. 弹出文件夹选择对话框
2. 自动打开浏览器
3. 一键保存所有商品
"""

import os
import re
import json
import time
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread


class TaobaoSaverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("淘宝店铺MHTML保存器")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # 变量
        self.save_dir = tk.StringVar(value="")
        self.shop_url = tk.StringVar(value="https://coppertistwu.jiyoujia.com/search.htm")
        self.delay = tk.IntVar(value=3)
        self.max_items = tk.IntVar(value=100)
        self.is_running = False
        self.driver = None

        self.setup_ui()

    def setup_ui(self):
        # 标题
        title = tk.Label(self.root, text="🏪 淘宝店铺MHTML保存器", font=("微软雅黑", 16, "bold"))
        title.pack(pady=10)

        # 主框架
        main_frame = tk.Frame(self.root, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 保存文件夹选择
        dir_frame = tk.LabelFrame(main_frame, text="保存位置", font=("微软雅黑", 10))
        dir_frame.pack(fill=tk.X, pady=5)

        dir_input_frame = tk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.dir_entry = tk.Entry(dir_input_frame, textvariable=self.save_dir, font=("微软雅黑", 9))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = tk.Button(dir_input_frame, text="浏览...", command=self.browse_folder,
                               font=("微软雅黑", 9), bg="#ff5000", fg="white", bd=0, padx=10)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # 店铺URL
        url_frame = tk.LabelFrame(main_frame, text="店铺搜索页URL", font=("微软雅黑", 10))
        url_frame.pack(fill=tk.X, pady=5)

        self.url_entry = tk.Entry(url_frame, textvariable=self.shop_url, font=("微软雅黑", 9))
        self.url_entry.pack(fill=tk.X, padx=10, pady=5)

        # 设置
        settings_frame = tk.LabelFrame(main_frame, text="设置", font=("微软雅黑", 10))
        settings_frame.pack(fill=tk.X, pady=5)

        tk.Label(settings_frame, text="保存间隔(秒):", font=("微软雅黑", 9)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        tk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.delay, width=10, font=("微软雅黑", 9)).grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(settings_frame, text="最大商品数:", font=("微软雅黑", 9)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        tk.Spinbox(settings_frame, from_=1, to=1000, textvariable=self.max_items, width=10, font=("微软雅黑", 9)).grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # 按钮
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = tk.Button(btn_frame, text="▶ 开始保存", command=self.start_save,
                                   font=("微软雅黑", 11, "bold"), bg="#ff5000", fg="white",
                                   bd=0, padx=30, pady=8, cursor="hand2")
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = tk.Button(btn_frame, text="⏹ 停止", command=self.stop_save,
                                  font=("微软雅黑", 11), bg="#999", fg="white",
                                  bd=0, padx=30, pady=8, cursor="hand2", state="disabled")
        self.stop_btn.pack(side=tk.LEFT)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=560, mode="determinate")
        self.progress.pack(fill=tk.X, pady=5)

        self.status_label = tk.Label(main_frame, text="准备就绪", font=("微软雅黑", 9), fg="#666")
        self.status_label.pack(anchor="w")

        # 日志区域
        log_frame = tk.LabelFrame(main_frame, text="日志", font=("微软雅黑", 10))
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def browse_folder(self):
        """打开文件夹选择对话框"""
        folder = filedialog.askdirectory(title="选择保存文件夹")
        if folder:
            self.save_dir.set(folder)
            self.log(f"已选择保存文件夹: {folder}")

    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()

    def update_status(self, text, color="#666"):
        self.status_label.config(text=text, fg=color)
        self.root.update()

    def update_progress(self, current, total):
        if total > 0:
            percent = (current / total) * 100
            self.progress["value"] = percent
            self.update_status(f"进度: {current}/{total} ({percent:.1f}%)")
        self.root.update()

    def start_save(self):
        if not self.save_dir.get():
            messagebox.showwarning("提示", "请先选择保存文件夹！")
            return

        if not os.path.exists(self.save_dir.get()):
            messagebox.showwarning("提示", "保存文件夹不存在！")
            return

        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal", bg="#c62828")
        self.progress["value"] = 0

        # 在新线程中运行
        thread = Thread(target=self.run_saver)
        thread.daemon = True
        thread.start()

    def stop_save(self):
        self.is_running = False
        self.update_status("正在停止...", "#c62828")
        self.log("用户请求停止")

    def run_saver(self):
        try:
            self.save_products()
        except Exception as e:
            self.log(f"错误: {str(e)}")
            self.update_status(f"错误: {str(e)}", "#c62828")
        finally:
            self.is_running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled", bg="#999")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def save_products(self):
        from playwright.sync_api import sync_playwright

        save_dir = self.save_dir.get()
        shop_url = self.shop_url.get()
        delay = self.delay.get()
        max_items = self.max_items.get()

        self.log("=" * 50)
        self.log("开始保存任务")
        self.log(f"保存文件夹: {save_dir}")
        self.log(f"店铺URL: {shop_url}")
        self.log("=" * 50)

        with sync_playwright() as p:
            # 启动浏览器
            self.update_status("正在启动浏览器...", "#1976d2")
            self.log("正在启动浏览器...")

            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            # 隐藏自动化特征
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            try:
                # 打开店铺页面
                self.update_status("正在打开店铺页面...", "#1976d2")
                self.log("正在打开店铺页面...")
                page.goto(shop_url, wait_until='networkidle', timeout=30000)
                time.sleep(3)

                # 检查登录
                page_text = page.inner_text('body')
                if '请登录' in page_text and '亲，请登录' in page_text:
                    self.update_status("需要登录淘宝，请在浏览器中完成登录", "#ff9800")
                    self.log("需要登录淘宝，请在浏览器中完成登录...")
                    messagebox.showinfo("提示", "请在浏览器中登录淘宝，然后点击确定继续")
                    page.reload(wait_until='networkidle')
                    time.sleep(3)

                # 提取商品
                self.update_status("正在提取商品列表...", "#1976d2")
                self.log("正在提取商品列表...")

                all_products = []
                seen_ids = set()
                page_num = 1

                while self.is_running:
                    self.log(f"--- 第 {page_num} 页 ---")

                    # 滚动加载
                    for _ in range(3):
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        time.sleep(2)

                    # 提取商品链接
                    links = page.query_selector_all('a[href*="item.taobao.com/item.htm"]')
                    self.log(f"  找到 {len(links)} 个链接")

                    page_products = []
                    for link in links:
                        try:
                            href = link.get_attribute('href') or ''
                            title = (link.get_attribute('title') or link.inner_text() or '').strip()

                            match = re.search(r'id=(\d+)', href)
                            if not match:
                                continue
                            item_id = match.group(1)

                            if item_id in seen_ids:
                                continue
                            seen_ids.add(item_id)

                            if not title or len(title) < 3:
                                continue

                            if any(k in title for k in ['消费者保障', '保证金', '收藏店铺', '装修', '定金']):
                                continue

                            if href.startswith('//'):
                                href = 'https:' + href

                            page_products.append({"item_id": item_id, "title": title, "url": href})
                        except:
                            continue

                    self.log(f"  提取到 {len(page_products)} 个新商品")
                    all_products.extend(page_products)

                    # 显示前3个
                    for i, p in enumerate(page_products[:3]):
                        self.log(f"    {i+1}. {p['title'][:40]}...")

                    # 检查是否达到最大数量
                    if len(all_products) >= max_items:
                        all_products = all_products[:max_items]
                        self.log(f"  已达到最大商品数 {max_items}")
                        break

                    # 点击下一页
                    try:
                        next_btn = page.query_selector('a[title="下一页"]')
                        if next_btn and next_btn.is_visible():
                            next_btn.click()
                            time.sleep(5)
                            page_num += 1
                        else:
                            # URL翻页
                            current_url = page.url
                            match = re.search(r'[?&]page=(\d+)', current_url)
                            if match:
                                next_page = int(match.group(1)) + 1
                                next_url = re.sub(r'page=\d+', f'page={next_page}', current_url)
                                page.goto(next_url, wait_until='networkidle')
                                time.sleep(5)
                                page_num += 1
                            else:
                                self.log("  没有下一页了")
                                break
                    except Exception as e:
                        self.log(f"  翻页结束: {e}")
                        break

                    if page_num > 50:
                        break

                self.log(f"\n共提取 {len(all_products)} 个商品")

                if not all_products:
                    self.update_status("未找到商品", "#c62828")
                    return

                # 保存MHTML
                self.log(f"\n开始保存MHTML到: {save_dir}")
                self.log("-" * 50)

                success = 0
                fail = 0

                for i, product in enumerate(all_products):
                    if not self.is_running:
                        self.log("任务已停止")
                        break

                    self.update_progress(i + 1, len(all_products))
                    self.log(f"\n[{i+1}/{len(all_products)}] {product['title'][:40]}...")

                    try:
                        page.goto(product['url'], wait_until='networkidle', timeout=30000)
                        time.sleep(3)

                        # 滚动页面
                        for _ in range(3):
                            page.evaluate("window.scrollBy(0, 500)")
                            time.sleep(1)

                        # 保存MHTML
                        title_clean = re.sub(r'[\\/:*?"<>|]', '_', product['title'])[:80]
                        filename = f"{title_clean}_{product['item_id']}-淘宝网.mhtml"
                        filepath = os.path.join(save_dir, filename)

                        # 使用CDP保存MHTML
                        client = page.context.new_cdp_session(page)
                        response = client.send("Page.captureSnapshot", {"format": "mhtml"})
                        mhtml = response.get("data", "")

                        if mhtml:
                            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                                f.write(mhtml)

                            size = os.path.getsize(filepath)
                            self.log(f"  ✅ {filename} ({size//1024} KB)")
                            success += 1
                        else:
                            self.log(f"  ❌ MHTML内容为空")
                            fail += 1

                    except Exception as e:
                        self.log(f"  ❌ 失败: {str(e)[:60]}")
                        fail += 1

                    # 延迟
                    if i < len(all_products) - 1 and self.is_running:
                        time.sleep(delay)

                # 汇总
                self.log(f"\n{'='*50}")
                self.log("保存完成！")
                self.log(f"成功: {success}  失败: {fail}")
                self.log(f"保存位置: {save_dir}")
                self.log(f"{'='*50}")

                self.update_status(f"完成！成功: {success}, 失败: {fail}", "#388e3c")

                if success > 0:
                    messagebox.showinfo("完成", f"保存完成！\n成功: {success} 个\n失败: {fail} 个\n\n保存位置: {save_dir}")

            finally:
                browser.close()


def main():
    root = tk.Tk()
    app = TaobaoSaverGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
