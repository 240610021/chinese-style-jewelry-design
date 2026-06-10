#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
淘宝/天猫商品评价爬虫
功能：抓取指定商品的评价内容，用于情感分析和差评统计
适用：淘宝、天猫商品详情页
注意：淘宝评价有反爬机制，建议控制请求频率
"""

import requests
import json
import time
import random
import csv
import os
import re
from urllib.parse import urlencode
from datetime import datetime

# ============ 配置区域 ============

# 商品ID（需要手动获取）
# 获取方法：打开商品详情页 → URL中找到 "id=123456789" → 123456789就是商品ID
#
# 琢匠已确认爆款商品（建议优先抓取）：
# 1. 山鬼剑狮吊坠（铜款）- 天猫爆款，常卖价¥159
#    搜索：天猫搜"琢匠 山鬼剑狮" → 复制商品ID
# 2. 饕餮纹手镯（s925银款）- 高端款¥2098，18K点金定制
#    搜索：天猫搜"琢匠 饕餮纹手镯" → 复制商品ID
# 3. 背云三通文玩配饰 - 低价引流款¥26起
#    搜索：淘宝搜"琢匠 背云三通" → 复制商品ID
# 4. 虎啸三通配饰（925银）- 文玩配件¥98
#    搜索：淘宝搜"琢匠 虎啸三通" → 复制商品ID
#
ITEM_ID = "884440625712"  # 山鬼剑狮吊坠

# 商品名称（用于文件名）
ITEM_NAME = "琢匠_山鬼剑狮吊坠"

# 请求头（模拟浏览器）
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": f"https://detail.tmall.com/item.htm?id={ITEM_ID}",
    "Cookie": "thw=cn; aui=2027319991; arms_uid=8c80ab10-852c-48c5-9198-057eaa94bcc4; wwUserTip=false; _hvn_lgc_=0; t=c99716aea141b0efebf0cd8cfec73e61; _tb_token_=e67330496eb45; sca=738cd5aa; havana_sdkSilent=1780997540743; cna=W3twIm1ZODMCAQ6ZDBZxVAaU; 3PcFlag=1780968747872; sn=; csg=ab76eff2; lgc=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; cancelledSubSites=empty; dnk=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; existShop=MTc4MDk2ODc0OQ%3D%3D; tracknick=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; _cc_=U%2BGCWk%2F7og%3D%3D; _l_g_=Ug%3D%3D; sg=418; _nk_=%5Cu5317%5Cu6597%5Cu706C%5Cu661F%5Cu8FB02014; sdkSilent=1780998340041; mtop_partitioned_detect=1; _m_h5_tk=5404b0c867e474a3a01bfc84eb82a849_1780996038673; _m_h5_tk_enc=41e0777b3e25ef355fa9c3ab0ee5fa2d; havana_lgc_exp=1812096076929; fastSlient=1780992076929; uc1=cookie14=UoYWPUm84tyVWQ%3D%3D&existShop=false&pas=0&cookie21=VT5L2FSpdeCjwGS%2FFqZpWg%3D%3D&cookie15=V32FPkk%2Fw0dUvg%3D%3D&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D; xlly_s=1; isg=BPX1oGF985MrhBThapBHxJFIEXGvcqmEIpeENXcZOWygThRAOsGXVYnemhL4FcE8; tfstk=hEdwk_9GBNOjfv19hcxWaVjqN1LO4hVbGsssKHSHylZ6oi120n-VftmO1I-ekUP6cdgAns-B4txfcFgV6sC0obYY4GLHJZDnnEmkWFCYJ0iSNbM4Y5pvI-jDm6fhPZfcmnVi8MbVy-qMms0e-MIhmsfDme0FkMjcisxm8ebYfSJLVpHe4e2fJwdFSmIkS-N0iB7aVgYZzSmZk54O0MdoAv8dYdx1JnlrYsKpnnb2xkmfBEveYN-6YYq8iw-7lAoHMn-9BUrnFBp6TTAe2PhHZjOeBhOgbqp9GHp2bKcumIodYUW5hzVqadA2AFdK1JusAe9JvtkbZCk93p-MTw7Ecs64hr7-GCwYH9fR8gg15-eAIwQFV2uUH-BhvwSS5N1..",  # 已填写
}

# 代理设置（可选）
PROXY = {
    # "http": "http://127.0.0.1:7890",
    # "https": "http://127.0.0.1:7890",
}

# 请求间隔（秒）
DELAY_MIN = 2
DELAY_MAX = 5

# 输出目录
OUTPUT_DIR = "output"

# 评价类型：all(全部), good(好评), neutral(中评), bad(差评)
REVIEW_TYPE = "all"

# 最大抓取页数
MAX_PAGES = 50

# ============ 核心代码 ============

class TaobaoReviewSpider:
    """淘宝/天猫评价爬虫"""
    
    def __init__(self, item_id, item_name, headers, proxy=None):
        self.item_id = item_id
        self.item_name = item_name
        self.headers = headers
        self.proxy = proxy or {}
        self.session = requests.Session()
        self.reviews = []
        
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
    
    def _get_random_delay(self):
        return random.uniform(DELAY_MIN, DELAY_MAX)
    
    def _make_request(self, url, params=None):
        try:
            time.sleep(self._get_random_delay())
            response = self.session.get(
                url,
                headers=self.headers,
                params=params,
                proxies=self.proxy,
                timeout=30
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def _parse_review_json(self, json_data):
        """解析评价JSON数据"""
        reviews = []
        
        if "rateDetail" not in json_data:
            return reviews
        
        rate_list = json_data["rateDetail"].get("rateList", [])
        
        for item in rate_list:
            review = {
                "review_id": item.get("id", ""),
                "user_nick": item.get("displayUserNick", ""),
                "rating": item.get("rate", ""),  # 评分
                "content": item.get("rateContent", ""),  # 评价内容
                "date": item.get("rateDate", ""),  # 评价时间
                "sku_info": item.get("auctionSku", ""),  # 购买的SKU
                "append_content": "",  # 追评内容
                "append_date": "",  # 追评时间
                "pics": ",".join([pic.get("url", "") for pic in item.get("pics", [])]),  # 图片
                "useful": item.get("useful", 0),  # 有用数
                "reply": item.get("reply", ""),  # 商家回复
            }
            
            # 追评
            append = item.get("appendComment", {})
            if append:
                review["append_content"] = append.get("content", "")
                review["append_date"] = append.get("dayAfterConfirm", "")
            
            reviews.append(review)
        
        return reviews
    
    def get_reviews(self, page=1):
        """
        获取评价数据
        淘宝评价API（可能随时变更）
        """
        # 淘宝评价API URL
        api_url = "https://rate.taobao.com/feedRateList.htm"
        
        params = {
            "auctionNumId": self.item_id,
            "userNumId": "",  # 卖家ID，可选
            "currentPageNum": page,
            "pageSize": 20,
            "rateType": "",  # 空=全部, 1=好评, 0=中评, -1=差评
            "orderType": "sort_weight",  # 默认排序
            "attribute": "",
            "sku": "",
            "hasSku": "false",
            "folded": "0",
            "callback": "jsonp_tbcrate_reviews_list",
        }
        
        # 根据评价类型调整参数
        if REVIEW_TYPE == "good":
            params["rateType"] = "1"
        elif REVIEW_TYPE == "neutral":
            params["rateType"] = "0"
        elif REVIEW_TYPE == "bad":
            params["rateType"] = "-1"
        
        response = self._make_request(api_url, params)
        if not response:
            return []
        
        # 解析JSONP响应
        text = response.text
        # 去除JSONP回调函数名
        json_str = re.search(r'\((.*)\)', text, re.DOTALL)
        if json_str:
            try:
                data = json.loads(json_str.group(1))
                reviews = self._parse_review_json(data)
                print(f"第{page}页: 获取 {len(reviews)} 条评价")
                return reviews
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return []
        else:
            print("无法解析响应数据")
            return []
    
    def crawl_all_reviews(self):
        """抓取所有评价"""
        print(f"开始抓取商品 [{self.item_name}] 的评价...")
        print(f"商品ID: {self.item_id}")
        print(f"评价类型: {REVIEW_TYPE}")
        print("=" * 60)
        
        for page in range(1, MAX_PAGES + 1):
            reviews = self.get_reviews(page)
            
            if not reviews:
                print(f"第{page}页无数据，可能已到达最后一页")
                break
            
            self.reviews.extend(reviews)
            
            # 检查是否还有下一页
            if len(reviews) < 20:
                print("已到达最后一页")
                break
        
        print(f"\n抓取完成！共获取 {len(self.reviews)} 条评价")
        return self.reviews
    
    def analyze_reviews(self):
        """简单分析评价数据"""
        if not self.reviews:
            print("没有数据可分析")
            return
        
        total = len(self.reviews)
        
        # 评分分布
        ratings = {}
        for r in self.reviews:
            rate = r.get("rating", "未知")
            ratings[rate] = ratings.get(rate, 0) + 1
        
        # 关键词统计
        keywords = {
            "品控": ["质量", "瑕疵", "做工", "粗糙", "瑕疵", "问题"],
            "售后": ["客服", "退货", "换货", "售后", "服务"],
            "物流": ["快递", "物流", "发货", "包装", "破损"],
            "设计": ["设计", "好看", "漂亮", "丑", "图片", "实物"],
            "价格": ["贵", "便宜", "值", "不值", "性价比", "价格"],
            "尺寸": ["大小", "尺寸", "合适", "不合适", "偏大", "偏小"],
        }
        
        keyword_stats = {k: 0 for k in keywords}
        
        for r in self.reviews:
            content = r.get("content", "")
            for category, words in keywords.items():
                for word in words:
                    if word in content:
                        keyword_stats[category] += 1
                        break
        
        print("\n" + "=" * 60)
        print("评价分析结果")
        print("=" * 60)
        print(f"总评价数: {total}")
        print("\n评分分布:")
        for rate, count in sorted(ratings.items()):
            pct = count / total * 100
            print(f"  {rate}星: {count}条 ({pct:.1f}%)")
        
        print("\n关键词提及频次:")
        for category, count in sorted(keyword_stats.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            print(f"  {category}: {count}条 ({pct:.1f}%)")
        
        # 输出差评示例
        bad_reviews = [r for r in self.reviews if r.get("rating") in ["1", "2", "-1"]]
        if bad_reviews:
            print(f"\n差评示例 (共{len(bad_reviews)}条):")
            for i, r in enumerate(bad_reviews[:5], 1):
                print(f"\n  [{i}] {r['date']} {r['rating']}星")
                print(f"      {r['content'][:100]}...")
    
    def save_to_csv(self, filename=None):
        """保存到CSV"""
        if not self.reviews:
            print("没有数据可保存")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/{self.item_name}_reviews_{REVIEW_TYPE}_{timestamp}.csv"
        
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=self.reviews[0].keys())
            writer.writeheader()
            writer.writerows(self.reviews)
        
        print(f"\n已保存 {len(self.reviews)} 条评价到: {filename}")
    
    def save_to_json(self, filename=None):
        """保存到JSON"""
        if not self.reviews:
            print("没有数据可保存")
            return
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/{self.item_name}_reviews_{REVIEW_TYPE}_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.reviews, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(self.reviews)} 条评价到: {filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("淘宝/天猫商品评价爬虫")
    print("=" * 60)
    
    # 如果未配置商品ID，提示输入
    global ITEM_ID, ITEM_NAME
    if ITEM_ID == "123456789":
        print("\n请提供商品信息:")
        ITEM_ID = input("商品ID (从商品URL中获取): ").strip()
        ITEM_NAME = input("商品名称 (用于文件名): ").strip() or "未知商品"
    
    # 初始化爬虫
    spider = TaobaoReviewSpider(ITEM_ID, ITEM_NAME, HEADERS, PROXY)
    
    # 抓取评价
    spider.crawl_all_reviews()
    
    # 分析评价
    if spider.reviews:
        spider.analyze_reviews()
        spider.save_to_csv()
        spider.save_to_json()
    else:
        print("未获取到评价数据，请检查配置")


if __name__ == "__main__":
    main()
